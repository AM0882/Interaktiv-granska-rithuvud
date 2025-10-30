import streamlit as st
from streamlit_drawable_canvas import st_canvas
import fitz  # PyMuPDF
import pandas as pd
import io

st.set_page_config(page_title="PDF Text Extractor", layout="wide")

st.title("📐 PDF Drawing Text Extractor")

uploaded_files = st.file_uploader("Upload PDF drawings", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    sample_pdf = uploaded_files[0]
    doc = fitz.open(stream=sample_pdf.read(), filetype="pdf")
    page = doc.load_page(0)
    pix = page.get_pixmap()
    img_bytes = pix.tobytes("png")

    st.subheader("Step 1: Select regions to extract text from")
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        background_image=img_bytes,
        update_streamlit=True,
        height=pix.height,
        width=pix.width,
        drawing_mode="rect",
        key="canvas",
    )

    if canvas_result.json_data and "objects" in canvas_result.json_data:
        boxes = [
            {
                "x0": obj["left"],
                "y0": obj["top"],
                "x1": obj["left"] + obj["width"],
                "y1": obj["top"] + obj["height"]
            }
            for obj in canvas_result.json_data["objects"]
        ]

        st.success(f"{len(boxes)} regions selected.")

        if st.button("Extract text and export to Excel"):
            data = []

            for file in uploaded_files:
                doc = fitz.open(stream=file.read(), filetype="pdf")
                page = doc.load_page(0)
                entry = {"filename": file.name}

                for i, box in enumerate(boxes):
                    rect = fitz.Rect(box["x0"], box["y0"], box["x1"], box["y1"])
                    text = page.get_textbox(rect).strip()
                    entry[f"Box {i+1}"] = text

                data.append(entry)

            df = pd.DataFrame(data)
            st.dataframe(df)

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False)
            st.download_button("Download Excel", data=output.getvalue(), file_name="extracted_text.xlsx")