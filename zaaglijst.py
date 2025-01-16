import streamlit as st

def zaaglijst_berekenen(profielen, zaag_lengte):
    zaag_stukken = []
    for lengte, aantal in profielen:
        zaag_stukken.extend([lengte] * aantal)

    zaag_stukken.sort(reverse=True)
    zaag_profiles = []

    while zaag_stukken:
        current_profile = []
        remaining_length = zaag_lengte

        for stuk in zaag_stukken[:]:
            if stuk <= remaining_length:
                current_profile.append(stuk)
                remaining_length -= stuk
                zaag_stukken.remove(stuk)

        zaag_profiles.append(current_profile)

    restmateriaal = zaag_lengte - sum(current_profile)
    geoptimaliseerde_zaaglijst = []
    vorige_profiel = None
    aantal = 0

    for profiel in zaag_profiles:
        if profiel == vorige_profiel:
            aantal += 1
        else:
            if vorige_profiel is not None:
                geoptimaliseerde_zaaglijst.append((vorige_profiel, aantal))
            vorige_profiel = profiel
            aantal = 1

    if vorige_profiel is not None:
        geoptimaliseerde_zaaglijst.append((vorige_profiel, aantal))

    return geoptimaliseerde_zaaglijst, restmateriaal, len(zaag_profiles)

def generate_export_content(zaaglijst, totaal_zaagprofielen, restmateriaal, profielen, totale_lengte_meters):
    content = "Toegevoegde Profielen\n"
    for lengte, aantal in profielen:
        content += f"Lengte: {lengte}, Aantal: {aantal}\n"

    content += "\nGeoptimaliseerde Zaaglijst\n"
    for index, (profiel, aantal) in enumerate(zaaglijst, 1):
        content += f"Zaagprofiel {index}: {profiel} x {aantal}\n"
    
    content += f"\nTotaal aantal benodigde zaaglengtes: {totaal_zaagprofielen}\n"
    content += f"Totaal lengte in meters: {totale_lengte_meters} m\n"
    content += f"Restmateriaal: {restmateriaal} mm\n"
    return content

def main():
    if 'profielen' not in st.session_state:
        st.session_state.profielen = []

    st.title("Zaaglijst Berekening")

    st.header("Voer de profiel lengtes en aantallen in")

    with st.form(key='profielen_form'):
        lengte = st.number_input("Profiel Lengte (in mm)", min_value=1, step=1)
        aantal = st.number_input("Aantal stukken", min_value=1, step=1)

        submit_button = st.form_submit_button("Voeg profiel toe")

        if submit_button and lengte > 0 and aantal > 0:
            st.session_state.profielen.append((lengte, aantal))
            st.success(f"Profiel van lengte {lengte} en aantal {aantal} is toegevoegd.")

    if len(st.session_state.profielen) > 0:
        st.subheader("Toegevoegde profielen")
        for i, (lengte, aantal) in enumerate(st.session_state.profielen, start=1):
            st.write(f"Lengte: {lengte}, Aantal: {aantal}")

    st.header("Bepaal de beschikbare zaaglengte")
    zaag_lengte = st.number_input("Beschikbare zaaglengte (in mm)", min_value=1, step=1)

    if st.button("Bereken Zaaglijst"):
        if len(st.session_state.profielen) > 0 and zaag_lengte > 0:
            zaaglijst, afval, totaal_zaagprofielen = zaaglijst_berekenen(st.session_state.profielen, zaag_lengte)

            # Bereken de totale lengte in meters
            totale_lengte = sum(lengte * aantal for lengte, aantal in st.session_state.profielen)
            totale_lengte_meters = totale_lengte / 1000

            st.subheader("Geoptimaliseerde Zaaglijst")
            for index, (profiel, aantal) in enumerate(zaaglijst, 1):
                st.write(f"Zaagprofiel {index}: {profiel} x {aantal}")

            st.write(f"\nTotaal aantal benodigde zaaglengtes: {totaal_zaagprofielen}")
            st.write(f"Totaal lengte in meters: {totale_lengte_meters:.2f} m")
            st.write(f"Restmateriaal: {afval} mm")

            # Genereer exportinhoud
            content = generate_export_content(zaaglijst, totaal_zaagprofielen, afval, st.session_state.profielen, totale_lengte_meters)

            # Downloadknop voor txt-bestand
            st.download_button(
                label="Exporteer naar TXT",
                data=content,
                file_name="zaaglijst.txt",
                mime="text/plain",
            )
        else:
            st.error("Voer eerst profielen en zaaglengte in!")

if __name__ == "__main__":
    main()

