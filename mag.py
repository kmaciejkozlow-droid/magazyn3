import streamlit as st

st.set_page_config(page_title="Prosty magazyn", page_icon="📦")

# Inicjalizacja magazynu w pamięci (lista słowników)
if "magazyn" not in st.session_state:
    st.session_state.magazyn = []

st.title("📦 Prosty magazyn towarów")
st.caption("Dane przechowywane są tylko w pamięci aplikacji (brak zapisu do plików).")

# --- Formularz dodawania towaru ---
with st.form("dodaj_towar"):
    st.subheader("Dodaj towar")
    nazwa = st.text_input("Nazwa towaru")
    ilosc = st.number_input("Ilość", min_value=0, step=1)
    cena = st.number_input("Cena za sztukę", min_value=0.0, step=0.01)
    dodaj = st.form_submit_button("Dodaj")

    if dodaj and nazwa:
        st.session_state.magazyn.append({
            "nazwa": nazwa,
            "ilosc": ilosc,
            "cena": cena
        })
        st.success(f"Dodano towar: {nazwa}")

# --- Wyświetlanie magazynu ---
st.subheader("Stan magazynu")

if st.session_state.magazyn:
    for i, towar in enumerate(st.session_state.magazyn):
        col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
        col1.write(towar["nazwa"])
        col2.write(f"Ilość: {towar['ilosc']}")
        col3.write(f"Cena: {towar['cena']} zł")
        if col4.button("❌", key=f"usun_{i}"):
            st.session_state.magazyn.pop(i)
            st.experimental_rerun()
else:
    st.info("Magazyn jest pusty.")

# --- Podsumowanie ---
st.subheader("Podsumowanie")
wartosc = sum(t["ilosc"] * t["cena"] for t in st.session_state.magazyn)
st.write(f"Łączna wartość magazynu: **{wartosc:.2f} zł**")

st.divider()
st.caption("Aplikacja demonstracyjna – idealna do uruchomienia na Streamlit Cloud z GitHuba.")
# --- Formularz usuwania ilości towaru ---
st.divider()
st.subheader("Usuń / wydaj towar")

if st.session_state.magazyn:
    nazwy = [t["nazwa"] for t in st.session_state.magazyn]

    with st.form("usun_towar"):
        wybrany = st.selectbox("Wybierz towar", nazwy)
        ilosc_do_usuniecia = st.number_input(
            "Ilość do usunięcia",
            min_value=1,
            step=1
        )
        usun = st.form_submit_button("Usuń z magazynu")

        if usun:
            for t in st.session_state.magazyn:
                if t["nazwa"] == wybrany:
                    if ilosc_do_usuniecia >= t["ilosc"]:
                        st.session_state.magazyn.remove(t)
                        st.success(f"Usunięto cały towar: {wybrany}")
                    else:
                        t["ilosc"] -= ilosc_do_usuniecia
                        st.success(
                            f"Usunięto {ilosc_do_usuniecia} szt. z {wybrany}"
                        )
                    st.experimental_rerun()
else:
    st.info("Brak towarów do usunięcia.")
