def gen_summary_pipeline(short_url, num_buckets=24, num_top_countries=5, num_top_referrers=5):
    pipeline = [
        {"$match": {"short_url": short_url}},
        {
            "$facet": {
                "total_clicks": [{"$count": "total"}],
                "timeline": [
                    {
                        "$bucketAuto": {
                            "groupBy": "$timestamp",
                            "buckets": num_buckets,
                            "output": {"count": {"$sum": 1}},
                        }
                    }
                ],
                "top_countries": [
                    {"$group": {"_id": "$country", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": num_top_countries},
                ],
                "top_referrers": [
                    {"$group": {"_id": "$referer", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": num_top_referrers},
                ],
                "browser_distribution": [{"$group": {"_id": "$browserType", "count": {"$sum": 1}}}],
            }
        },
    ]
    return pipeline


def gen_overview_pipeline(short_url):
    pipeline = [
        {"$match": {"short_url": short_url}},
        {
            "$group": {
                "_id": "overview",
                "clicks": {"$sum": {"$cond": [{"$eq": ["$type", "click"]}, 1, 0]}},
                "scans": {"$sum": {"$cond": [{"$eq": ["$type", "scan"]}, 1, 0]}},
                "last_activity": {"$max": "$timestamp"},
                "total_engagement": {"$sum": 1},
            }
        },
    ]
    return pipeline


def gen_referrer_pipeline(short_url: str):
    pipeline = [
        {"$match": {"short_url": short_url}},
        {"$group": {"_id": "$referer", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$project": {"referral": "$_id", "amount": "$count", "_id": 0}},
    ]
    return pipeline


def gen_countries_and_cities_pipeline(short_url: str):
    pipeline = [
        {"$match": {"short_url": short_url}},
        {"$group": {"_id": {"country": "$country", "city": "$city"}, "count": {"$sum": 1}}},
        {"$group": {"_id": "$_id.country", "cities": {"$push": {"city": "$_id.city", "count": "$count"}}}},
        {"$project": {"_id": 0, "country": "$_id", "cities": 1}},
        {"$group": {"_id": None, "countries": {"$push": {"country": "$country", "cities": "$cities"}}}},
        {"$project": {"_id": 0, "countries": 1}},
    ]
    return pipeline


def gen_timeseries_pipeline(short_url: str):
    pipeline = [
        {"$match": {"short_url": short_url, "timestamp": {"$exists": True, "$type": "date"}}},
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$timestamp"},
                    "month": {"$month": "$timestamp"},
                    "day": {"$dayOfMonth": "$timestamp"},
                    "hour": {"$hour": "$timestamp"},
                },
                "count": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "date": {
                    "$dateFromParts": {
                        "year": "$_id.year",
                        "month": "$_id.month",
                        "day": "$_id.day",
                        "hour": "$_id.hour",
                    }
                },
                "count": 1,
            }
        },
        {"$sort": {"date": 1}},
    ]
    return pipeline
