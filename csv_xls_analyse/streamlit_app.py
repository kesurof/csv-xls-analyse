import io
import streamlit as st

from .core import merge_csv_files, create_export_excel, analyse_consumption


def main():
    st.title('Analyse de consommation')

    uploaded_files = st.file_uploader(
        'Choisissez des fichiers CSV ou ZIP',
        type=['zip', 'csv'],
        accept_multiple_files=True,
    )

    if uploaded_files:
        temp_files = []
        for f in uploaded_files:
            data = f.read()
            temp_path = f.name
            with open(temp_path, 'wb') as tmp:
                tmp.write(data)
            temp_files.append(temp_path)
    else:
        temp_files = []

    if st.button('Lancer la conversion'):
        if not temp_files:
            st.warning('Aucun fichier sélectionné')
        else:
            df = merge_csv_files(temp_files)
            excel_buffer = io.BytesIO()
            create_export_excel(df, excel_buffer)
            st.session_state['excel'] = excel_buffer.getvalue()
            st.success('Conversion terminée')

    if 'excel' in st.session_state:
        st.download_button('Télécharger le fichier Excel', st.session_state['excel'], file_name='Analyse de Parc.xlsx')


if __name__ == '__main__':
    main()
