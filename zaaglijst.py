import streamlit as st
from typing import List, Tuple

# Type aliases
Profile = Tuple[int, int]           # (lengte in mm, aantal)
ZaagLijstItem = Tuple[List[int], int]  # (lijst met stukken, aantal keer dit patroon)


def zaaglijst_berekenen(profielen: List[Profile], zaag_lengte: int) -> Tuple[List[ZaagLijstItem], int, int, int]:
    """
    Bereken een geoptimaliseerde zaaglijst op basis van de ingevoerde profielen en de beschikbare zaaglengte.

    Args:
        profielen (List[Profile]): Lijst met tuples (lengte, aantal) voor elk profiel.
        zaag_lengte (int): De lengte van het zaagprofiel in mm.

    Returns:
        Tuple:
            - geoptimaliseerde zaaglijst als een lijst van tuples (lijst van stukken, aantal keer dit patroon)
            - restmateriaal van het laatste profiel in mm
            - totaal aantal gebruikte zaagprofielen
            - totaal restmateriaal (afval) van alle profielen in mm
    """
    # Maak een lijst van alle individuele stukken op basis van de profielen
    zaag_stukken = []
    for lengte, aantal in profielen:
        zaag_stukken.extend([lengte] * aantal)

    # Sorteer de stukken in aflopende volgorde
    zaag_stukken.sort(reverse=True)
    gebruikte_zaagprofielen = []  # Lijst met lijsten, elk profiel bevat de stukken die erin geplaatst zijn

    # Greedy algoritme: vul telkens een nieuw zaagprofiel
    while zaag_stukken:
        huidig_profiel = []
        resterende_lengte = zaag_lengte

        # Loop over een kopie van de lijst om veilig items te verwijderen
        for stuk in zaag_stukken[:]:
            if stuk <= resterende_lengte:
                huidig_profiel.append(stuk)
                resterende_lengte -= stuk
                zaag_stukken.remove(stuk)

        gebruikte_zaagprofielen.append(huidig_profiel)

    # Bereken het restmateriaal van het laatste profiel (indien aanwezig)
    restmateriaal = zaag_lengte - sum(gebruikte_zaagprofielen[-1]) if gebruikte_zaagprofielen else zaag_lengte

    # Bereken het totale restmateriaal (afval) van alle profielen
    totaal_afval = sum(zaag_lengte - sum(profiel) for profiel in gebruikte_zaagprofielen)

    # Groepeer profielen met hetzelfde patroon
    geoptimaliseerde_zaaglijst: List[ZaagLijstItem] = []
    vorige_profiel = None
    aantal_gelijk = 0

    for profiel in gebruikte_zaagprofielen:
        if profiel == vorige_profiel:
            aantal_gelijk += 1
        else:
            if vorige_profiel is not None:
                geoptimaliseerde_zaaglijst.append((vorige_profiel, aantal_gelijk))
            vorige_profiel = profiel
            aantal_gelijk = 1

    if vorige_profiel is not None:
        geoptimaliseerde_zaaglijst.append((vorige_profiel, aantal_gelijk))

    totaal_zaagprofielen = len(gebruikte_zaagprofielen)
    return geoptimaliseerde_zaaglijst, restmateriaal, totaal_zaagprofielen, totaal_afval


def generate_export_content(
    zaaglijst: List[ZaagLijstItem],
    totaal_zaagprofielen: int,
    restmateriaal: int,
    totaal_afval: int,
    profielen: List[Profile],
    totale_lengte_meters: float
) -> str:
    """
    Genereer de exportinhoud als een tekstbestand.

    Args:
        zaaglijst (List[ZaagLijstItem]): De geoptimaliseerde zaaglijst.
        totaal_zaagprofielen (int): Totaal aantal benodigde zaagprofielen.
        restmateriaal (int): Restmateriaal van het laatste profiel in mm.
        totaal_afval (int): Totaal restmateriaal van alle profielen in mm.
        profielen (List[Profile]): De ingevoerde profielen.
        totale_lengte_meters (float): Totale lengte van alle profielen in meters.

    Returns:
        str: De te exporteren inhoud.
    """
    content = "Toegevoegde Profielen:\n"
    for lengte, aantal in profielen:
        content += f" - Lengte: {lengte} mm, Aantal: {aantal}\n"

    content += "\nGeoptimaliseerde Zaaglijst:\n"
    for index, (profiel, aantal) in enumerate(zaaglijst, 1):
        content += f"Zaagprofiel {index}: {profiel} x {aantal}\n"
    
    content += f"\nTotaal aantal benodigde zaagprofielen: {totaal_zaagprofielen}\n"
    content += f"Totaal lengte in meters: {totale_lengte_meters:.2f} m\n"
    content += f"Restmateriaal van laatste profiel: {restmateriaal} mm\n"
    content += f"Totaal restmateriaal (afval): {totaal_afval} mm\n"
    return content


def display_profielen(profielen: List[Profile]) -> List[Profile]:
    """
    Toon de huidige lijst met toegevoegde profielen met een optie om elk profiel te verwijderen.
    """
    st.subheader("Toegevoegde Profielen")
    nieuwe_profielen = []
    for idx, (lengte, aantal) in enumerate(profielen):
        cols = st.columns([3, 1])
        cols[0].write(f"Lengte: {lengte} mm, Aantal: {aantal}")
        if cols[1].button("Verwijder", key=f"remove_{idx}"):
            st.info(f"Profiel met lengte {lengte} mm verwijderd.")
            continue  # Sla dit profiel over
        nieuwe_profielen.append((lengte, aantal))
    return nieuwe_profielen


def add_profiel(profielen: List[Profile], lengte: int, aantal: int) -> List[Profile]:
    """
    Voeg een profiel toe aan de lijst.
    """
    profielen.append((lengte, aantal))
    st.success(f"Profiel van lengte {lengte} mm en aantal {aantal} is toegevoegd.")
    return profielen


def main():
    st.title("Zaaglijst Berekening")

    # Initialiseer de profielen als ze nog niet bestaan in session_state
    if "profielen" not in st.session_state:
        st.session_state.profielen = []  # type: List[Profile]

    st.header("Voer de profiel lengtes en aantallen in")
    with st.form(key="profielen_form"):
        lengte = st.number_input("Profiel Lengte (in mm)", min_value=1, step=1, format="%d")
        aantal = st.number_input("Aantal stukken", min_value=1, step=1, format="%d")
        submit_button = st.form_submit_button("Voeg profiel toe")

        if submit_button:
            if lengte > 0 and aantal > 0:
                st.session_state.profielen = add_profiel(st.session_state.profielen, lengte, aantal)
            else:
                st.error("Lengte en aantal moeten groter zijn dan 0.")

    if st.session_state.profielen:
        st.session_state.profielen = display_profielen(st.session_state.profielen)
    else:
        st.info("Nog geen profielen toegevoegd.")

    st.header("Bepaal de beschikbare zaaglengte")
    zaag_lengte = st.number_input("Beschikbare zaaglengte (in mm)", min_value=1, step=1, format="%d")

    if st.button("Bereken Zaaglijst"):
        if st.session_state.profielen and zaag_lengte > 0:
            try:
                zaaglijst, restmateriaal, totaal_zaagprofielen, totaal_afval = zaaglijst_berekenen(
                    st.session_state.profielen, zaag_lengte
                )

                totale_lengte = sum(lengte * aantal for lengte, aantal in st.session_state.profielen)
                totale_lengte_meters = totale_lengte / 1000

                st.subheader("Geoptimaliseerde Zaaglijst")
                for index, (profiel, aantal) in enumerate(zaaglijst, 1):
                    st.write(f"Zaagprofiel {index}: {profiel} x {aantal}")

                st.write(f"Totaal aantal benodigde zaagprofielen: {totaal_zaagprofielen}")
                st.write(f"Totaal lengte in meters: {totale_lengte_meters:.2f} m")
                st.write(f"Restmateriaal van laatste profiel: {restmateriaal} mm")
                st.write(f"Totaal restmateriaal (afval): {totaal_afval} mm")

                content = generate_export_content(
                    zaaglijst, totaal_zaagprofielen, restmateriaal, totaal_afval,
                    st.session_state.profielen, totale_lengte_meters
                )
                st.download_button(
                    label="Exporteer naar TXT",
                    data=content,
                    file_name="zaaglijst.txt",
                    mime="text/plain",
                )
            except Exception as e:
                st.error(f"Er is een fout opgetreden tijdens de berekening: {e}")
        else:
            st.error("Voer eerst geldige profielen en zaaglengte in!")


if __name__ == "__main__":
    main()

