"""ShelfScan — Application Streamlit pour l'inventaire de bibliothèque."""

import copy
import logging
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)


def prepare_ocr_display_data(result: dict) -> list[dict]:
    """Prépare les données OCR pour affichage dans l'onglet OCR.

    Args:
        result: Résultat structuré du pipeline contenant une clé ``books``.

    Returns:
        Liste de dicts avec les clés ``spine_id``, ``raw_text``,
        et ``confidence`` pour chaque tranche détectée.

    Raises:
        KeyError: Si la clé ``books`` est absente du résultat.
    """
    books = result["books"]
    return [
        {
            "spine_id": book["spine_id"],
            "raw_text": book["raw_text"],
            "confidence": book["confidence"],
        }
        for book in books
    ]


def prepare_inventory_dataframe(result: dict) -> pd.DataFrame:
    """Prépare le DataFrame de l'inventaire pour affichage interactif.

    Args:
        result: Résultat structuré du pipeline contenant une clé ``books``.

    Returns:
        DataFrame avec les colonnes Titre, Auteur, ISBN, Confiance.

    Raises:
        KeyError: Si la clé ``books`` est absente du résultat.
    """
    books = result["books"]
    rows = [
        {
            "Titre": book["title"],
            "Auteur": book["author"],
            "ISBN": book["isbn"],
            "Confiance": book["confidence"],
        }
        for book in books
    ]
    return pd.DataFrame(rows)


def apply_manual_corrections(result: dict, corrections: dict) -> dict:
    """Applique les corrections manuelles au résultat du pipeline.

    Args:
        result: Résultat structuré du pipeline contenant une clé ``books``.
        corrections: Dict de corrections ``{spine_id: {"title": ..., "author": ...}}``.

    Returns:
        Nouveau résultat avec les corrections appliquées.
        Les livres corrigés portent le flag ``manually_corrected: True``.
    """
    corrected = copy.deepcopy(result)
    spine_id_to_book = {book["spine_id"]: book for book in corrected["books"]}

    for spine_id, fields in corrections.items():
        if spine_id not in spine_id_to_book:
            continue
        book = spine_id_to_book[spine_id]
        for key, value in fields.items():
            book[key] = value
        book["manually_corrected"] = True

    return corrected


def prepare_editable_dataframe(result: dict) -> pd.DataFrame:
    """Prépare un DataFrame éditable avec colonne de statut de modification.

    Args:
        result: Résultat structuré du pipeline contenant une clé ``books``.

    Returns:
        DataFrame avec les colonnes Titre, Auteur, ISBN, Confiance, Modifié.

    Raises:
        KeyError: Si la clé ``books`` est absente du résultat.
    """
    books = result["books"]
    rows = [
        {
            "Titre": book["title"],
            "Auteur": book["author"],
            "ISBN": book["isbn"],
            "Confiance": book["confidence"],
            "Modifié": book.get("manually_corrected", False),
        }
        for book in books
    ]
    return pd.DataFrame(rows)


def _run_pipeline_with_progress(image_path: str) -> dict:
    """Exécute le pipeline avec barre de progression Streamlit.

    Args:
        image_path: Chemin vers l'image sur disque.

    Returns:
        Résultat structuré du pipeline.

    Raises:
        RuntimeError: Si le pipeline échoue (encapsule l'erreur originale).
    """
    from src.pipeline import run_pipeline

    progress_bar = st.progress(0, text="Initialisation du pipeline...")

    progress_bar.progress(10, text="Prétraitement de l'image...")

    try:
        result = run_pipeline(image_path)
    except Exception as exc:
        progress_bar.empty()
        raise RuntimeError(
            f"Erreur lors de l'exécution du pipeline : {exc}"
        ) from exc

    progress_bar.progress(100, text="Traitement terminé.")
    return result


def _display_original_tab(image_bytes: bytes, file_name: str) -> None:
    """Affiche l'onglet Original avec image et métadonnées.

    Args:
        image_bytes: Contenu brut du fichier image.
        file_name: Nom du fichier uploadé.
    """
    from PIL import Image
    import io

    st.image(image_bytes, caption="Image uploadée", use_container_width=True)

    img = Image.open(io.BytesIO(image_bytes))
    width, height = img.size
    st.markdown("**Métadonnées de l'image**")
    col1, col2, col3 = st.columns(3)
    col1.metric("Largeur", f"{width} px")
    col2.metric("Hauteur", f"{height} px")
    col3.metric("Fichier", file_name)


def _display_preprocess_tab(image_path: str) -> None:
    """Affiche l'onglet Prétraitement avec l'image après CLAHE.

    Args:
        image_path: Chemin vers l'image sur disque.
    """
    from src.preprocess import preprocess
    from src.visualization import bgr_to_rgb

    preprocessed = preprocess(image_path)
    preprocessed_rgb = bgr_to_rgb(preprocessed)
    st.image(
        preprocessed_rgb,
        caption="Image après prétraitement (CLAHE)",
        use_container_width=True,
    )


def _display_segmentation_tab(image_path: str) -> None:
    """Affiche l'onglet Segmentation avec bounding boxes.

    Args:
        image_path: Chemin vers l'image sur disque.
    """
    from src.preprocess import preprocess
    from src.visualization import bgr_to_rgb, draw_spine_boxes, segment_with_positions

    preprocessed = preprocess(image_path)
    spines = segment_with_positions(preprocessed)
    annotated = draw_spine_boxes(preprocessed, spines)
    annotated_rgb = bgr_to_rgb(annotated)
    st.image(
        annotated_rgb,
        caption="Segmentation des tranches de livres",
        use_container_width=True,
    )
    st.info(f"{len(spines)} tranche(s) détectée(s).")


def _display_ocr_tab(result: dict) -> None:
    """Affiche l'onglet OCR avec le texte détecté par tranche.

    Args:
        result: Résultat structuré du pipeline.
    """
    ocr_data = prepare_ocr_display_data(result)
    if not ocr_data:
        st.warning("Aucun texte détecté.")
        return

    for item in ocr_data:
        with st.expander(f"Tranche #{item['spine_id']}", expanded=True):
            st.markdown(f"**Texte brut :** {item['raw_text']}")
            st.markdown(f"**Confiance :** {item['confidence']:.2%}")


def _display_inventory_tab(result: dict, image_stem: str) -> None:
    """Affiche l'onglet Inventaire avec tableau éditable et export CSV.

    Args:
        result: Résultat structuré du pipeline.
        image_stem: Nom du fichier image sans extension (pour le nom CSV).
    """
    # Initialiser les corrections manuelles en session state
    if "manual_corrections" not in st.session_state:
        st.session_state.manual_corrections = {}

    # Appliquer les corrections existantes
    corrected_result = apply_manual_corrections(
        result, st.session_state.manual_corrections
    )
    df = prepare_editable_dataframe(corrected_result)

    st.subheader("Résultats de l'inventaire")

    if not df.empty:
        # Colonnes éditables : Titre, Auteur, ISBN
        column_config = {
            "Confiance": st.column_config.NumberColumn(
                "Confiance", format="%.2f", disabled=True
            ),
            "Modifié": st.column_config.CheckboxColumn(
                "Modifié", disabled=True
            ),
        }
        edited_df = st.data_editor(
            df,
            column_config=column_config,
            use_container_width=True,
            num_rows="fixed",
            key="inventory_editor",
        )

        # Détecter les modifications et mettre à jour les corrections
        books = corrected_result["books"]
        for idx, book in enumerate(books):
            spine_id = book["spine_id"]
            edited_row = edited_df.iloc[idx]
            changes = {}
            if edited_row["Titre"] != book["title"]:
                changes["title"] = edited_row["Titre"]
            if edited_row["Auteur"] != book["author"]:
                changes["author"] = edited_row["Auteur"]
            if edited_row["ISBN"] != book["isbn"]:
                changes["isbn"] = edited_row["ISBN"]
            if changes:
                existing = st.session_state.manual_corrections.get(spine_id, {})
                existing.update(changes)
                st.session_state.manual_corrections[spine_id] = existing

        # Export avec corrections appliquées
        export_df = edited_df.drop(columns=["Modifié"])
        csv_content = export_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Exporter en CSV",
            data=csv_content,
            file_name=f"{image_stem}_inventaire.csv",
            mime="text/csv",
        )
    else:
        st.dataframe(df, use_container_width=True)


def main():
    """Point d'entrée de l'application ShelfScan."""
    st.set_page_config(
        page_title="ShelfScan",
        page_icon="\U0001f4da",
        layout="wide",
    )

    st.title("ShelfScan — Inventaire de bibliothèque")
    st.markdown("Uploadez une photo d'étagère pour identifier les livres.")

    uploaded_file = st.file_uploader(
        "Choisir une image",
        type=["jpeg", "jpg", "png"],
        help="Formats acceptés : JPEG, PNG",
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.getvalue()
        file_name = uploaded_file.name
        image_stem = Path(file_name).stem

        # Sauvegarder temporairement sur disque pour le pipeline
        suffix = Path(file_name).suffix
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=suffix
        ) as tmp_file:
            tmp_file.write(image_bytes)
            tmp_path = tmp_file.name

        # Exécuter le pipeline
        pipeline_result = None
        pipeline_error = None
        try:
            pipeline_result = _run_pipeline_with_progress(tmp_path)
        except RuntimeError as exc:
            pipeline_error = str(exc)

        # Afficher les résultats par onglets
        tabs = st.tabs([
            "Original",
            "Prétraitement",
            "Segmentation",
            "OCR",
            "Inventaire",
        ])

        with tabs[0]:
            _display_original_tab(image_bytes, file_name)

        with tabs[1]:
            try:
                _display_preprocess_tab(tmp_path)
            except Exception as exc:
                st.error(f"Erreur lors du prétraitement : {exc}")

        with tabs[2]:
            try:
                _display_segmentation_tab(tmp_path)
            except Exception as exc:
                st.error(f"Erreur lors de la segmentation : {exc}")

        with tabs[3]:
            if pipeline_error is not None:
                st.error(pipeline_error)
            elif pipeline_result is not None:
                _display_ocr_tab(pipeline_result)

        with tabs[4]:
            if pipeline_error is not None:
                st.error(pipeline_error)
            elif pipeline_result is not None:
                _display_inventory_tab(pipeline_result, image_stem)


if __name__ == "__main__":
    main()
