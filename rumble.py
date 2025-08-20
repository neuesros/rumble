import streamlit as st
import random
import pandas as pd
import os

# ELO-Parameter
def expected_score(rating_a, rating_b):
    return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))

def update_elo(rating_winner, rating_loser, k=32):
    expected_win = expected_score(rating_winner, rating_loser)
    expected_loss = expected_score(rating_loser, rating_winner)
    return (
        rating_winner + k * (1 - expected_win),
        rating_loser + k * (0 - expected_loss),
    )

# Session State vorbereiten
if "books" not in st.session_state:
    st.session_state.books = {}
if "pair" not in st.session_state:
    st.session_state.pair = []

st.title("📚 Buch-Duell: Was soll ich als Nächstes lesen?")

# Bücherliste eingeben oder hochladen
st.sidebar.header("Bücherliste eingeben oder hochladen")
option = st.sidebar.radio("Eingabemethode wählen:", ("Manuelle Eingabe", "CSV-Upload"))

if option == "Manuelle Eingabe":
    manual_input = st.sidebar.text_area("Buchtitel (einer pro Zeile):")
    if st.sidebar.button("Liste übernehmen"):
        lines = [line.strip() for line in manual_input.split("\n") if line.strip()]
        st.session_state.books = {title: 1000 for title in lines}
elif option == "CSV-Upload":
    uploaded_file = st.sidebar.file_uploader("CSV mit Buchtiteln hochladen", type="csv")
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        if "title" in df.columns:
            st.session_state.books = {title: 1000 for title in df["title"].dropna()}
        else:
            st.warning("CSV muss eine Spalte 'title' enthalten.")

# Duell anzeigen
if len(st.session_state.books) >= 2:
    if not st.session_state.pair:
        st.session_state.pair = random.sample(list(st.session_state.books.keys()), 2)

    book1, book2 = st.session_state.pair
    col1, col2 = st.columns(2)

    with col1:
        if st.button(book1):
            win, lose = book1, book2
    with col2:
        if st.button(book2):
            win, lose = book2, book1

    if "win" in locals():
        rating_win = st.session_state.books[win]
        rating_lose = st.session_state.books[lose]
        new_win, new_lose = update_elo(rating_win, rating_lose)
        st.session_state.books[win] = round(new_win, 2)
        st.session_state.books[lose] = round(new_lose, 2)
        st.session_state.pair = []

    st.write("Aktuelles Ranking:")
    ranking = sorted(st.session_state.books.items(), key=lambda x: x[1], reverse=True)
    st.dataframe(pd.DataFrame(ranking, columns=["Buchtitel", "Punkte"]))
else:
    st.info("Bitte gib mindestens 2 Buchtitel ein, um das Duell zu starten.")
