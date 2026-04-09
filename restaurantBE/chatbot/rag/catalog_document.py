from decimal import Decimal, InvalidOperation
from typing import Any, Dict, Optional


class CatalogDocumentService:
    def build_category_document(self, category) -> Dict[str, Any]:
        vi_name = self._get_i18n_text(getattr(category, "name", {}), "vi")
        en_name = self._get_i18n_text(getattr(category, "name", {}), "en")
        vi_description = self._get_i18n_text(getattr(category, "description", {}), "vi")
        en_description = self._get_i18n_text(getattr(category, "description", {}), "en")
        is_active = bool(getattr(category, "is_active", True))

        content = "\n".join(
            [
                "=== DANH MUC MON AN / FOOD CATEGORY ===",
                f"Category ID: {category.id}",
                f"Ten tieng Viet: {vi_name or 'Chua co'}",
                f"English name: {en_name or 'N/A'}",
                f"Mo ta tieng Viet: {vi_description or 'Chua co'}",
                f"English description: {en_description or 'N/A'}",
                f"Dang hoat dong: {'Co' if is_active else 'Khong'}",
                f"Active: {'Yes' if is_active else 'No'}",
                f"Tu khoa tim kiem: {vi_name} | {en_name}",
                "Ngon ngu ho tro: tieng Viet, English",
            ]
        ).strip()

        title = f"{vi_name or ''} / {en_name or ''}".strip(" /")

        return {
            "id": f"category__{category.id}",
            "content": content,
            "metadata": {
                "source_type": "CATEGORY",
                "source": "catalog_category",
                "object_id": str(category.id),
                "title": title or f"Category {category.id}",
                "language": "vi_en",
                "is_active": is_active,
                "category_id": int(category.id),
                "category_name_vi": vi_name,
                "category_name_en": en_name,
            },
        }

    def build_dish_document(
        self, dish, category: Optional[object] = None
    ) -> Dict[str, Any]:
        vi_name = self._get_i18n_text(getattr(dish, "name", {}), "vi")
        en_name = self._get_i18n_text(getattr(dish, "name", {}), "en")
        vi_description = self._get_i18n_text(getattr(dish, "description", {}), "vi")
        en_description = self._get_i18n_text(getattr(dish, "description", {}), "en")

        category_db_id = self._extract_category_db_id(dish=dish, category=category)

        vi_category_name = ""
        en_category_name = ""
        vi_category_description = ""
        en_category_description = ""

        if category is not None:
            vi_category_name = self._get_i18n_text(getattr(category, "name", {}), "vi")
            en_category_name = self._get_i18n_text(getattr(category, "name", {}), "en")
            vi_category_description = self._get_i18n_text(
                getattr(category, "description", {}), "vi"
            )
            en_category_description = self._get_i18n_text(
                getattr(category, "description", {}), "en"
            )

        price_vnd = self._to_decimal(getattr(dish, "price", None))
        price_usd = self._to_decimal(getattr(dish, "price_usd", None))

        status = str(getattr(dish, "status", "") or "").strip()
        image = str(getattr(dish, "image", "") or "").strip()

        content = "\n".join(
            [
                "=== THONG TIN MON AN / DISH INFORMATION ===",
                f"Dish ID: {dish.id}",
                f"Ten tieng Viet: {vi_name or 'Chua co'}",
                f"English name: {en_name or 'N/A'}",
                f"Danh muc tieng Viet: {vi_category_name or 'Chua phan loai'}",
                f"Category in English: {en_category_name or 'Uncategorized'}",
                f"Mo ta danh muc tieng Viet: {vi_category_description or 'Chua co'}",
                f"Category description in English: {en_category_description or 'N/A'}",
                f"Gia VND: {self._format_vnd(price_vnd)}",
                f"Price USD: {self._format_usd(price_usd)}",
                f"Trang thai: {status or 'UNKNOWN'}",
                f"Status: {status or 'UNKNOWN'}",
                f"Mo ta tieng Viet: {vi_description or 'Chua co'}",
                f"English description: {en_description or 'N/A'}",
                f"Hinh anh: {image or 'Khong co'}",
                f"Image URL: {image or 'N/A'}",
                f"Tu khoa tim kiem: {vi_name} | {en_name} | {vi_category_name} | {en_category_name}",
                "Ngon ngu ho tro: tieng Viet, English",
            ]
        ).strip()

        title = f"{vi_name or ''} / {en_name or ''}".strip(" /")

        metadata = {
            "source_type": "DISH",
            "source": "catalog_dish",
            "object_id": str(dish.id),
            "title": title or f"Dish {dish.id}",
            "language": "vi_en",
            "dish_id": int(dish.id),
            "category_id": int(category_db_id) if category_db_id is not None else -1,
            "category_name_vi": vi_category_name,
            "category_name_en": en_category_name,
            "status": status or "UNKNOWN",
            "price_vnd": float(price_vnd) if price_vnd is not None else 0.0,
            "price_usd": float(price_usd) if price_usd is not None else 0.0,
        }

        return {
            "id": f"dish__{dish.id}",
            "content": content,
            "metadata": metadata,
        }

    def _get_i18n_text(self, value: Any, lang: str) -> str:
        if isinstance(value, dict):
            return str(value.get(lang, "") or "").strip()
        if value is None:
            return ""
        return str(value).strip()

    def _to_decimal(self, value: Any) -> Optional[Decimal]:
        if value in (None, ""):
            return None
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            return None

    def _format_vnd(self, value: Optional[Decimal]) -> str:
        if value is None:
            return "N/A"
        return f"{int(value):,} VND"

    def _format_usd(self, value: Optional[Decimal]) -> str:
        if value is None:
            return "N/A"
        return f"{value:.2f} USD"

    def _extract_category_db_id(
        self, dish, category: Optional[object]
    ) -> Optional[int]:
        if category is not None and getattr(category, "id", None) is not None:
            return int(category.id)

        raw_fk_id = getattr(dish, "category_id_id", None)
        if raw_fk_id is not None:
            return int(raw_fk_id)

        relation = getattr(dish, "category_id", None)
        if relation is not None and getattr(relation, "id", None) is not None:
            return int(relation.id)

        return None
