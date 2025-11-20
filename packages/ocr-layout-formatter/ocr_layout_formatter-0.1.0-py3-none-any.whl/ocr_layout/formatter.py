import logging
from typing import List, Dict

# Create module logger
logger = logging.getLogger(__name__)


class Formatter:
    """
    Formatter for OCR JSON to spatial text conversion.

    Converts OCR data to formatted text that preserves document layout
    without index tags.

    Example:
        >>> formatter = Formatter()
        >>> formatted_text = formatter.format(ocr_data)
    """

    def __init__(self,
                gap_threshold: int = 40,
                y_threshold: int = 15):

        if not isinstance(gap_threshold, (int, float)):
            raise TypeError(f"gap_threshold must be a number, got {type(gap_threshold).__name__}")

        if not isinstance(y_threshold, (int, float)):
            raise TypeError(f"y_threshold must be a number, got {type(y_threshold).__name__}")

        self.gap_threshold = gap_threshold
        self.y_threshold = y_threshold


    def format(self, ocr_list: List[Dict]) -> str:
        """
        Convert OCR JSON data to formatted text preserving document layout.

        Args:
            ocr_list (List[Dict]): List of OCR data for each page

        Returns:
            str: Formatted text preserving the original document layout
        """

        formatted_pages = []

        for page_num, page_data in enumerate(ocr_list, 1):
            logger.debug(f"Processing page {page_num}")

            try:
                cleaned_page = self._normalize_ocr_page(page_data)
                logger.debug(f"Page {page_num}: Found {len(cleaned_page['text_lines'])} text lines")
                grouped_lines = self._group_texts_by_line(cleaned_page["text_lines"])

                page_lines = []
                for line_group in grouped_lines:
                    segments = self._split_line_into_segments(line_group["texts"])

                    if not segments:
                        continue

                    # Join segments in the same line with tabs
                    line_text = "\t".join([seg['text'] for seg in segments])
                    page_lines.append(line_text)

                if page_lines:
                    page_text = "\n".join(page_lines)
                    formatted_pages.append(f"--- Page {page_num} ---\n{page_text}")

            except Exception as e:
                logger.error(f"Error processing page {page_num}: {e}")
                raise ValueError(f"Error processing page {page_num}: {e}")

        logger.info(f"Formatted {len(formatted_pages)} pages successfully")
        return "\n\n".join(formatted_pages)

    def _normalize_ocr_page(self, page_data: Dict) -> Dict:
        """
        Clean and validate OCR data for a single page.

        Args:
            page_data (Dict): Raw OCR data for one page

        Returns:
            Dict: Cleaned OCR data with structure:
                {
                    "text_lines": [{"text": str, "bbox": list}],
                    "image_bbox": [x1, y1, x2, y2]
                }
        """

        # Extract from nested "result" structure if present
        if "result" in page_data and isinstance(page_data["result"], list):
            if page_data["result"]:
                ocr_data = page_data["result"][0]
            else:
                ocr_data = {"text_lines": [], "image_bbox": None}
        else:
            ocr_data = page_data

        # Filter valid text_lines
        valid_text_lines = []
        raw_text_lines = ocr_data.get("text_lines", [])

        if not isinstance(raw_text_lines, list):
            raw_text_lines = []

        for line in raw_text_lines:
            if not isinstance(line, dict):
                continue

            # Check if text exists and not empty after strip
            text = line.get("text", "")
            if not isinstance(text, str) or not text.strip():
                continue

            # Check if bbox exists and valid
            bbox = line.get("bbox")
            if not self._is_valid_bbox(bbox):
                continue

            # Add to valid lines with standardized structure
            valid_text_lines.append({
                "text": text,
                "bbox": list(bbox),
            })

        # Get image_bbox
        image_bbox = ocr_data.get("image_bbox", None)
        if not self._is_valid_bbox(image_bbox):
            image_bbox = None

        normalize_dict = {
            "text_lines": valid_text_lines,
            "image_bbox": list(image_bbox) if image_bbox is not None else None
        }

        return normalize_dict

    def _is_valid_bbox(self, bbox) -> bool:
        """Check if bbox is valid: list/tuple of 4 numeric values with positive area."""
        if bbox is None:
            return False
        if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
            return False
        try:
            x1, y1, x2, y2 = map(float, bbox)
            return (x2 > x1) and (y2 > y1)
        except (ValueError, TypeError):
            return False

    def _group_texts_by_line(self, text_lines: List[Dict]) -> List[Dict]:
        """
        Group texts on the same line based on Y coordinate proximity.

        Args:
            text_lines (List[Dict]): List of text_lines from normalize_ocr_page

        Returns:
            List[Dict]: List of grouped lines with structure:
                [{"y_pos": float, "texts": [...]}, ...]
        """
        if not text_lines or not isinstance(text_lines, list):
            return []

        # Calculate Y center point for each text
        texts_with_y = []
        for text_item in text_lines:

            bbox = text_item.get("bbox", [])
            y_center = (bbox[1] + bbox[3]) / 2
            texts_with_y.append((y_center, text_item))

        # Group by Y threshold
        groups = {}
        for y_center, text_item in texts_with_y:
            assigned = False
            # Find existing group within threshold range
            for group_y in list(groups.keys()):
                if abs(y_center - group_y) <= self.y_threshold:
                    groups[group_y].append(text_item)
                    assigned = True
                    break

            if not assigned:
                groups[y_center] = [text_item]

        grouped_lines = []
        for y_pos in sorted(groups.keys()):
            texts_in_group = groups[y_pos]

            texts_in_group.sort(key=lambda t: t.get("bbox", [0])[0])

            avg_y_pos = sum(
                (text.get("bbox", None)[1] + text.get("bbox", None)[3]) / 2
                for text in texts_in_group
            ) / len(texts_in_group)

            grouped_lines.append({
                "y_pos": avg_y_pos,
                "texts": texts_in_group
            })

        grouped_lines.sort(key=lambda group: group["y_pos"])

        return grouped_lines

    def _split_line_into_segments(self, texts_in_line: List[Dict]) -> List[Dict]:
        """
        Split a line into segments based on X gap between text boxes.

        Args:
            texts_in_line (List[Dict]): List of texts on the same line

        Returns:
            List[Dict]: List of segments with structure:
                [{"text": str}]
        """

        if not texts_in_line or not isinstance(texts_in_line, list):
            return []

        # Filter valid texts and sort by X position
        valid_texts = []

        for text_item in texts_in_line:
            valid_texts.append(text_item)


        sorted_texts = sorted(valid_texts, key=lambda t: t["bbox"][0])

        segments = []
        current_group = [sorted_texts[0]]

        for i in range(1, len(sorted_texts)):
            current_text = sorted_texts[i]
            prev_text = current_group[-1]

            # Calculate gap
            gap = current_text["bbox"][0] - prev_text["bbox"][2]

            if gap > self.gap_threshold:
                segment = self._create_segment_from_texts(current_group)
                segments.append(segment)
                current_group = [current_text]

            else:
                current_group.append(current_text)

        if current_group:
            segment = self._create_segment_from_texts(current_group)
            segments.append(segment)

        return segments

    def _create_segment_from_texts(self, texts: List[Dict]) -> Dict:
        """
        Create a segment from a list of texts.

        Args:
            texts (List[Dict]): List of text objects to merge

        Returns:
            Dict: Segment object with merged text
        """

        text_parts = [t.get("text", "").strip() for t in texts if t.get("text", "").strip()]
        combined_text = " ".join(text_parts)

        return {
            "text": combined_text,
        }
