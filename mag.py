import streamlit as st
from supabase import create_client

# --- Inicjalizacja Supabase ---
@st.cache_resource
def init_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"]
    )

supabase = init_supabase()

# --- Test połączenia ---
try:
    supabase.table("magazyn").select("id").limit(1).execute()
    st.success("✅ Połączono z Supabase")
except Exception as e:
    st.error(f"❌ Błąd połączenia: {e}")

# --- Konfiguracja strony ---
st.set_page_config(page_title="Prosty magazyn", page_icon="📦")
st.title("📦 Prosty magazyn towarów")

# --- Pobranie produktów z Supabase ---
if "magazyn" not in st.session_state:
    result = supabase.table("magazyn").select("*").execute()
    if result.error:
        st.session_state.magazyn = []
        st.error(f"Błąd pobierania danych: {result.error.message}")
    else:
        st.session_state.magazyn = result.data

# --- Formularz dodawania towaru ---
with st.form("dodaj_towar"):
    st.subheader("Dodaj towar")
    nazwa = st.text_input("Nazwa towaru")
    ilosc = st.number_input("Ilość", min_value=0, step=1)
    cena = st.number_input("Cena za sztukę", min_value=0.0, step=0.01)
    dodaj = st.form_submit_button("Dodaj")

    if dodaj and nazwa:
        response = supabase.table("magazyn").insert({
            "nazwa": nazwa,
            "ilosc": ilosc,
            "cena": cena
        }).execute()

        if response.error:
            st.error(f"Błąd dodawania: {response.error.message}")
        else:
            st.success(f"Dodano towar: {nazwa}")
            # Odświeżenie listy magazynu
            st.session_state.magazyn.append(response.data[0])

# --- Wyświetlanie magazynu ---
st.subheader("Stan magazynu")
if st.session_state.magazyn:
    for i, towar in enumerate(st.session_state.magazyn):
        col1, col2, col3, col4 = st.columns([4, 2, 2, 1])
        col1.write(towar["nazwa"])
        col2.write(f"Ilość: {towar['ilosc']}")
        col3.write(f"Cena: {towar['cena']} zł")
        if col4.button("❌", key=f"usun_{i}"):
            response = supabase.table("magazyn").delete().eq("id", towar["id"]).execute()
            if response.error:
                st.error(f"Błąd usuwania: {response.error.message}")
            else:
                st.session_state.magazyn.pop(i)
                st.experimental_rerun()
else:
    st.info("Magazyn jest pusty.")

# --- Podsumowanie wartości magazynu ---
st.subheader("Podsumowanie")
wartosc = sum(t["ilosc"] * float(t["cena"]) for t in st.session_state.magazyn)
st.write(f"Łączna wartość magazynu: **{wartosc:.2f} zł**")

st.divider()
st.caption("Aplikacja demonstracyjna – dane zapisywane w Supabase.")

# --- Formularz usuwania / wydania towaru ---
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
                    nowa_ilosc = t["ilosc"] - ilosc_do_usuniecia
                    if nowa_ilosc <= 0:
                        response = supabase.table("magazyn").delete().eq("id", t["id"]).execute()
                        if response.error:
                            st.error(f"Błąd usuwania: {response.error.message}")
                        else:
                            st.session_state.magazyn.remove(t)
                            st.success(f"Usunięto cały towar: {wybrany}")
                    else:
                        response = supabase.table("magazyn").update({
                            "ilosc": nowa_ilosc
                        }).eq("id", t["id"]).execute()
                        if response.error:
                            st.error(f"Błąd aktualizacji: {response.error.message}")
                        else:
                            t["ilosc"] = nowa_ilosc
                            st.success(f"Usunięto {ilosc_do_usuniecia} szt. z {wybrany}")
                    st.rerun()
else:
    st.info("Brak towarów do usunięcia.")
