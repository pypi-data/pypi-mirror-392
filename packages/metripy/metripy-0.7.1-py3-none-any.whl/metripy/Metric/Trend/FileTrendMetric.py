class FileTrendMetric:
    def __init__(
        self,
        historical_loc: int,
        loc: int,
        historical_totalCc: int,
        totalCc: int,
        historical_avgCcPerFunction: float,
        avgCcPerFunction: float,
        historical_maintainabilityIndex: float,
        maintainabilityIndex: float,
        historical_avgLocPerFunction: float,
        avgLocPerFunction: float,
        historical_avg_cog_complexity_per_function: float,
        avg_cog_complexity_per_function: float,
    ):
        self.historical_loc = historical_loc
        self.loc_delta = loc - historical_loc

        self.historical_totalCc = historical_totalCc
        self.totalCc_delta = totalCc - historical_totalCc

        self.historical_avgCcPerFunction = historical_avgCcPerFunction
        self.avgCcPerFunction_delta = avgCcPerFunction - historical_avgCcPerFunction

        self.maintainabilityIndex_delta = (
            maintainabilityIndex - historical_maintainabilityIndex
        )
        self.historical_maintainabilityIndex = historical_maintainabilityIndex

        self.avgLocPerFunction_delta = avgLocPerFunction - historical_avgLocPerFunction
        self.historical_avgLocPerFunction = historical_avgLocPerFunction

        self.historical_avg_cog_complexity_per_function = (
            historical_avg_cog_complexity_per_function
        )
        self.avg_cog_complexity_per_function_delta = (
            avg_cog_complexity_per_function - historical_avg_cog_complexity_per_function
        )

    def to_dict(self) -> dict:
        return {
            "historical_loc": round(self.historical_loc, 2),
            "loc_delta": round(self.loc_delta, 2),
            "historical_totalCc": round(self.historical_totalCc, 2),
            "totalCc_delta": round(self.totalCc_delta, 2),
            "historical_avgCcPerFunction": round(self.historical_avgCcPerFunction, 2),
            "avgCcPerFunction_delta": round(self.avgCcPerFunction_delta, 2),
            "historical_avg_cog_complexity_per_function": round(
                self.historical_avg_cog_complexity_per_function, 2
            ),
            "avg_cog_complexity_per_function_delta": round(
                self.avg_cog_complexity_per_function_delta, 2
            ),
            "historical_maintainabilityIndex": round(
                self.historical_maintainabilityIndex, 2
            ),
            "maintainabilityIndex_delta": round(self.maintainabilityIndex_delta, 2),
            "historical_avgLocPerFunction": round(self.historical_avgLocPerFunction, 2),
            "avgLocPerFunction_delta": round(self.avgLocPerFunction_delta, 2),
        }
