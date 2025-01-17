import random
from maingame.models import Artifact, Dominion, Unit
from maingame.utils.give_stuff import give_dominion_unit


def give_random_unowned_artifact_to_dominion(dominion: Dominion):
    unowned_artifacts = []

    for artifact in Artifact.objects.filter(ruler=None):
        if dominion.faction_name == "Blessed Order" and artifact.name == "Death's True Name":
            pass
        else:
            unowned_artifacts.append(artifact)

    given_artifact = random.choice(unowned_artifacts)
    assign_artifact(given_artifact, dominion)

    return given_artifact


def assign_artifact(artifact: Artifact, new_owner: Dominion):
    if new_owner.faction_name == "Blessed Order" and artifact.name == "Death's True Name":
        pass
    else:
        artifact.ruler = new_owner

    if artifact.name == "The Eternal Egg of the Flame Princess":
        give_dominion_unit(new_owner, Unit.objects.get(ruler=None, name="Fireball"))
    elif artifact.name == "The Infernal Contract":
        give_dominion_unit(new_owner, Unit.objects.get(ruler=None, name="Imp"))

    artifact.save()