from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional

from ratisbona_utils.nonbraindead_enums import ObjectEnum
from ratisbona_utils.strings import align, Alignment, zip_longest_textcolumn


class InfiniteForm(ObjectEnum):
    """
    Enum for the infinitive forms of German verbs.
    """

    INFINITIV = {"uiname": "Infinitiv"}
    PARTIZIP_I = {"uiname": "Partizip_i"}
    PARTIZIP_II = {"uiname": "Partizip_ii"}


class Genus(ObjectEnum):
    MAENNLICH = {"uiname": "männlich"}
    WEIBLICH = {"uiname": "weiblich"}
    SAECHLICH = {"uiname": "sächlich"}


class VerbPerson(ObjectEnum):
    ERSTE = {"singular": "ich", "plural": "wir"}
    ZWEITE = {"singular": "du", "plural": "ihr"}
    DRITTE = {"singular": "er/sie/es", "plural": "sie"}

    def pronoun(self, singular: bool = True) -> str:
        """
        Returns the pronoun for the given person.
        """
        return self.singular if singular else self.plural


class Numerus(ObjectEnum):
    SINGULAR = {"uiname": "Singular"}
    PLURAL = {"uiname": "Plural"}


class Tempus(ObjectEnum):
    """
    Enum for the tenses in German.
    """
    PRAESENS = {"uiname": "Präsens"}
    PERFEKT = {"uiname": "Perfekt"}
    PRAETERITUM = {"uiname": "Präteritum"}
    PLUSQUAMPERFEKT = {"uiname": "Plusquamperfekt"}
    FUTUR_I = {"uiname": "Futur I"}
    FUTUR_II = {"uiname": "Futur II"}


class Diathese(ObjectEnum):
    """
    Enum for the diathesis (voice) in German.
    """

    AKTIV = {"uiname": "Aktiv"}
    PASSIV = {"uiname": "Passiv"}


class Modus(ObjectEnum):
    """
    Enum for the mood in German.
    """

    INDIKATIV = {"uiname": "Indikativ"}
    KONJUNKTIV_I = {"uiname": "Konjunktiv I"}
    KONJUNKTIV_II = {"uiname": "Konjunktiv II"}
    KONJUNKTIV_III = {"uiname": "Konjunktiv III"}
    IMPERATIV = {"uiname": "Imperativ"}


@dataclass(frozen=True)
class FiniteForm:
    person: VerbPerson  # 3
    genus: Genus  # 3
    tempus: Tempus  # 6
    modus: Modus  # 5
    numerus: Numerus  # 2
    diathese: Diathese  # 2


@dataclass(frozen=True)
class Verb:
    infinitiv: str
    praesens_stamm: str
    praeteritum: str
    partizip_ii: str
    hilfsverb: Optional[Verb]
    irregularities: dict[FiniteForm, str] = field(default_factory=dict)

    def _infinite_form(self, form: InfiniteForm) -> str:
        """
        Returns the infinite form of the verb.
        """
        if form == InfiniteForm.INFINITIV:
            return self.infinitiv
        if form == InfiniteForm.PARTIZIP_I:
            return f"{self.praesens_stamm}end"
        if form == InfiniteForm.PARTIZIP_II:
            return self.partizip_ii
        raise ValueError(f"Unknown infinite form: {form}")

    def _finite_form(self, form: FiniteForm) -> str:
        if form.modus == Modus.IMPERATIV:
            if form.numerus == Numerus.SINGULAR:
                return f"{self.praesens_stamm}e"
            if form.numerus == Numerus.PLURAL:
                return f"{self.praesens_stamm}t"
            raise ValueError(f"Unknown number: {form.numerus}")
        if form.modus == Modus.KONJUNKTIV_I:
            return "_konjunktiv_i(self, form)"
        if form.modus == Modus.KONJUNKTIV_II:
            return "_konjunktiv_ii(self, form)"
        if form.modus == Modus.INDIKATIV:
            return self._indikativ(form)

    def _indikativ_praesens_aktiv(self, form: FiniteForm) -> str:
        if form.numerus == Numerus.SINGULAR:
            if form.person == VerbPerson.ERSTE:
                retval = self.praesens_stamm
                if not self.praesens_stamm.endswith("e"):
                    retval += "e"
                return retval
            if form.person == VerbPerson.ZWEITE:
                return f"{self.praesens_stamm}st"
            if form.person == VerbPerson.DRITTE:
                return f"{self.praesens_stamm}t"
            raise ValueError(f"Unknown person: {form.person}")
        if form.numerus == Numerus.PLURAL:
            if form.person == VerbPerson.ERSTE:
                retval = self.praesens_stamm
                if not self.praesens_stamm.endswith("e"):
                    retval += "e"
                return retval + "n"
            if form.person == VerbPerson.ZWEITE:
                retval = self.praesens_stamm
                if not self.praesens_stamm.endswith("e"):
                    retval += "e"
                return retval + "t"
            if form.person == VerbPerson.DRITTE:
                retval = self.praesens_stamm
                if not self.praesens_stamm.endswith("e"):
                    retval += "e"
                return retval + "n"
            raise ValueError(f"Unknown person: {form.person}")
        raise ValueError(f"Unknown number: {form.numerus}")

    def _indikativ_praesens_passiv(self, form: FiniteForm) -> str:
        hilfsform = FiniteForm(
            person=form.person,
            genus=form.genus,
            tempus=form.tempus,
            modus=form.modus,
            numerus=form.numerus,
            diathese=Diathese.AKTIV,
        )
        return f"{werden.form(hilfsform)} {self.partizip_ii}"

    def _indikativ_praeteritum_aktiv(self, form: FiniteForm) -> str:
        if form.numerus == Numerus.SINGULAR:
            if form.person == VerbPerson.ERSTE:
                return self.praeteritum
            if form.person == VerbPerson.ZWEITE:
                return f"{self.praeteritum}st"
            if form.person == VerbPerson.DRITTE:
                return self.praeteritum
            raise ValueError(f"Unknown person: {form.person}")
        if form.numerus == Numerus.PLURAL:
            if form.person == VerbPerson.ERSTE:
                retval = self.praeteritum
                if not self.praeteritum.endswith("e"):
                    retval += "e"
                return retval + "n"
            if form.person == VerbPerson.ZWEITE:
                retval = self.praeteritum
                if not self.praeteritum.endswith("e"):
                    retval += "e"
                return retval + "t"
            if form.person == VerbPerson.DRITTE:
                retval = self.praeteritum
                if not self.praeteritum.endswith("e"):
                    retval += "e"
                return retval + "n"
            raise ValueError(f"Unknown person: {form.person}")
        raise ValueError(f"Unknown number: {form.numerus}")

    def _indikativ_praeteritum_passiv(self, form: FiniteForm) -> str:
        hilfsform = FiniteForm(
            person=form.person,
            genus=form.genus,
            tempus=form.tempus,
            modus=form.modus,
            numerus=form.numerus,
            diathese=Diathese.AKTIV,
        )
        return f"{werden.form(hilfsform)} {self.partizip_ii}"

    def _indikativ_perfekt_aktiv(self, form: FiniteForm) -> str:
        hilfsform1= FiniteForm(
            person=form.person,
            genus=form.genus,
            tempus=Tempus.PRAESENS,
            modus=form.modus,
            numerus=form.numerus,
            diathese=Diathese.AKTIV,
        )
        return f"{self.hilfsverb.form(hilfsform1)} {self.partizip_ii}"


    def _indikativ_perfekt_passiv(self, form: FiniteForm) -> str:
        hilfsform1 = FiniteForm(
            person=form.person,
            genus=form.genus,
            tempus=Tempus.PRAESENS,
            modus=form.modus,
            numerus=form.numerus,
            diathese=Diathese.AKTIV,
        )
        return f"{self.hilfsverb.form(hilfsform1)} {self.partizip_ii} worden"

    def _indikativ(self, form: FiniteForm) -> str:
        if form.tempus == Tempus.PRAESENS:
            return (
                self._indikativ_praesens_aktiv(form)
                if form.diathese == Diathese.AKTIV
                else self._indikativ_praesens_passiv(form)
            )

        if form.tempus == Tempus.PERFEKT:
            return (
                self._indikativ_perfekt_aktiv(form)
                if form.diathese == Diathese.AKTIV
                else self._indikativ_perfekt_passiv(form)
            )

        if form.tempus == Tempus.PRAETERITUM:
            return (
                self._indikativ_praeteritum_aktiv(form)
                if form.diathese == Diathese.AKTIV
                else self._indikativ_praeteritum_passiv(form)
            )

        if form.tempus == Tempus.FUTUR_I:
            return f"{self.hilfsverb} {self.infinitiv}"

        if form.tempus == Tempus.FUTUR_II:
            return f"{self.hilfsverb} {self.partizip_ii}"

        raise ValueError(f"Unknown tense: {form.tempus}")

    def form(self, form: FiniteForm | InfiniteForm) -> str:
        if isinstance(form, InfiniteForm):
            return self._infinite_form(form)
        elif isinstance(form, FiniteForm):
            if form in self.irregularities:
                return self.irregularities[form]
            return self._finite_form(form)
        else:
            raise ValueError(f"Unknown form type: {type(form)}")


haben = Verb(
    infinitiv="haben",
    praesens_stamm="hab",
    praeteritum="hatte",
    partizip_ii="gehabt",
    hilfsverb=None,
    irregularities={
        FiniteForm(
            person=VerbPerson.ZWEITE,
            genus=Genus.MAENNLICH,
            tempus=Tempus.PRAESENS,
            modus=Modus.INDIKATIV,
            numerus=Numerus.SINGULAR,
            diathese=Diathese.AKTIV,
        ): "hast",
        FiniteForm(
            person=VerbPerson.DRITTE,
            genus=Genus.MAENNLICH,
            tempus=Tempus.PRAESENS,
            modus=Modus.INDIKATIV,
            numerus=Numerus.SINGULAR,
            diathese=Diathese.AKTIV,
        ): "hat",
    },
)

def _sein_irreg():
    _tb = {
        "person": VerbPerson.ERSTE,
        "genus": Genus.MAENNLICH,
        "tempus": Tempus.PRAESENS,
        "modus": Modus.INDIKATIV,
        "numerus": Numerus.SINGULAR,
        "diathese": Diathese.AKTIV,
    }
    irreg = {}
    irreg[FiniteForm(**_tb)] = "bin"
    _tb["person"] = VerbPerson.ZWEITE
    irreg[FiniteForm(**_tb)] = "bist"
    _tb["person"] = VerbPerson.DRITTE
    irreg[FiniteForm(**_tb)] = "ist"
    _tb["person"] = VerbPerson.ERSTE
    _tb["numerus"] = Numerus.PLURAL
    irreg[FiniteForm(**_tb)] = "sind"
    _tb["person"] = VerbPerson.ZWEITE
    irreg[FiniteForm(**_tb)] = "seid"
    _tb["person"] = VerbPerson.DRITTE
    irreg[FiniteForm(**_tb)] = "sind"

    _tb["tempus"] = Tempus.PRAETERITUM
    _tb["numerus"] = Numerus.SINGULAR
    _tb["person"] = VerbPerson.ERSTE
    irreg[FiniteForm(**_tb)] = "war"
    _tb["person"] = VerbPerson.DRITTE
    irreg[FiniteForm(**_tb)] = "war"

    return irreg


sein = Verb(
    infinitiv="sein",
    praesens_stamm="sei",
    praeteritum="war",
    partizip_ii="gewesen",
    hilfsverb=None,
    irregularities=_sein_irreg()
)

werden = Verb(
    infinitiv="werden",
    praesens_stamm="werd",
    praeteritum="wurde",
    partizip_ii="geworden",
    hilfsverb=sein,
    irregularities={
        FiniteForm(
            person=VerbPerson.ZWEITE,
            genus=Genus.MAENNLICH,
            tempus=Tempus.PRAESENS,
            modus=Modus.INDIKATIV,
            numerus=Numerus.SINGULAR,
            diathese=Diathese.AKTIV,
        ): "wirst",
        FiniteForm(
            person=VerbPerson.DRITTE,
            genus=Genus.MAENNLICH,
            tempus=Tempus.PRAESENS,
            modus=Modus.INDIKATIV,
            numerus=Numerus.SINGULAR,
            diathese=Diathese.AKTIV,
        ): "wird",
        FiniteForm(
            person=VerbPerson.ZWEITE,
            genus=Genus.MAENNLICH,
            tempus=Tempus.PRAESENS,
            modus=Modus.INDIKATIV,
            numerus=Numerus.PLURAL,
            diathese=Diathese.AKTIV,
        ): "werdet"
    },
)

object.__setattr__(haben,"hilfsverb", haben)
object.__setattr__(sein,"hilfsverb", sein)


def main():
    # Example usage
    verb = Verb(
        infinitiv="gehen",
        praesens_stamm="geh",
        praeteritum="ging",
        partizip_ii="gegangen",
        hilfsverb=sein,
    )

    class TestEnum(Enum):
        ONE = auto()
        TWO = auto()

    for modus in Modus:
        print(align(modus.uiname, width=80, alignment=Alignment.CENTER))
        print("=" * 80)
        for tempus in Tempus:
            print(tempus.uiname.center(80))
            strings = []
            for diathese in Diathese:
                string = f"{diathese.uiname.center(38)}"
                string += "\n" + "-" * 38
                for anzahl in Numerus:
                    for person in VerbPerson:
                        form = FiniteForm(
                            person=person,
                            genus=Genus.MAENNLICH,
                            tempus=tempus,
                            modus=modus,
                            numerus=anzahl,
                            diathese=diathese,
                        )
                        string += f"\n{person.pronoun(anzahl==Numerus.SINGULAR)} {verb.form(form)}"
                strings.append(string)
            print(zip_longest_textcolumn(*strings))


if __name__ == "__main__":
    main()
