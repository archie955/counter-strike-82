import logging

from helpers import Position

from exceptions.app_exceptions import DataNotFoundError
from schemas import lineup_schemas

logger = logging.getLogger(__name__)


def test_pos_evaluation(
    pos: Position, player: lineup_schemas.Lineup_Player
) -> lineup_schemas.Adjusted_Player:
    adj_player = lineup_schemas.Adjusted_Player(
        name=player.name, team=player.team, major=player.major, hltv=0.96 * player.hltv
    )
    return adj_player


# TO UPDATE WITH ACTUAL MODELS/SCORING
def evaluate_lineup(lineup: lineup_schemas.Lineup):
    # Edit this error handling
    if not lineup:
        raise DataNotFoundError(datatype="Lineup")

    awper = test_pos_evaluation(Position.AWP, lineup.awp)
    support = test_pos_evaluation(Position.SUPPORT, lineup.support)
    opener = test_pos_evaluation(Position.OPEN, lineup.opener)
    closer = test_pos_evaluation(Position.CLOSE, lineup.closer)
    igl = test_pos_evaluation(Position.IGL, lineup.igl)

    # type: ignore
    igl_points = chem_evaluation(team=[awper, support, opener, closer], igl=igl)

    total_points = igl_points + awper.hltv + opener.hltv + closer.hltv + support.hltv

    return lineup_schemas.Final_Lineup(
        points=total_points
    )  # other arguments to fill out later


# then define evaluate user lineup which uses
# user dependency injection to compare to what is in the database, then put or dont.
