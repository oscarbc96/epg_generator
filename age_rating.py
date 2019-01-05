from enum import Enum

from utils import clean_string


class AgeRating(Enum):
    NOT_RECOMMENDED_FOR_CHILDREN_UNDER_18 = "18"
    NOT_RECOMMENDED_FOR_CHILDREN_UNDER_16 = "16"
    NOT_RECOMMENDED_FOR_CHILDREN_UNDER_12 = "12"
    NOT_RECOMMENDED_FOR_CHILDREN_UNDER_10 = "10"
    NOT_RECOMMENDED_FOR_CHILDREN_UNDER_7 = "7"
    SUITABLE_FOR_ALL_AUDIENCES = "todos"
    NOT_RATED = "-"

    @staticmethod
    def from_str(string):
        string = clean_string(string)

        for rating in AgeRating:
            if rating.value in string:
                return rating

        return AgeRating.NOT_RATED
