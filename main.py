import time
from datetime import datetime
import pymongo

from pycoinmarketcap import CoinMarketCap
import github


class CMC:
    def __init__(self, key: str):
        self.cmc = CoinMarketCap(key)

    def getLatestCryptocurrencyListings(self, limit, sortDir):
        return self.cmc.crypto_listings_latest(limit=limit, sort_dir=sortDir)

    def getCryptoGitRepo(self, crypto):
        if self.cmc.crypto_metadata(symbol=crypto).data[crypto]['urls']['source_code']:
            if "git" in self.cmc.crypto_metadata(symbol=crypto).data[crypto]['urls']['source_code'][0]:
                return '/'.join(
                    self.cmc.crypto_metadata(symbol=crypto).data[crypto]['urls']['source_code'][
                        0].split("/")[3:])
            else:
                return ""
        else:
            return ""


class Git:
    def __init__(self, key: str):
        self.git = github.Github(key)


def populateMongoWithDict(key, value, identifier, db_name, collection_name):
    settings = {
        'host': '',
        'database': db_name,
        'username': '',
        'password': '',
        'options': ''
    }

    example_doc = {'start': datetime.utcnow(), key: value, "identifier": identifier}

    try:
        conn = pymongo.MongoClient("mongodb://{username}:{password}@{host}/{database}?{options}".format(**settings))
    except Exception as ex:
        print("Error:", ex)
        exit('Failed to connect, terminating.')

    db = conn[db_name]
    collection = db[collection_name]

    doc_id = collection.insert_one(example_doc).inserted_id

    print("Heres the _id of the doc I inserted: %s." % doc_id)


def storeMetrics(limit: int, sortDir: str, identifier: str):
    c = CMC('')

    g = Git("")

    topCryptos = c.getLatestCryptocurrencyListings(limit, sortDir)

    for crypto in range(len(topCryptos.data)):
        try:
            gitRepo = c.getCryptoGitRepo(topCryptos.data[crypto]['symbol'])
            gitRepoObj = g.git.get_repo(gitRepo)
            if gitRepo and gitRepoObj:
                populateMongoWithDict(
                    gitRepo
                    ,
                    {
                        'commitsCount': gitRepoObj.get_commits().totalCount,
                        'issuesCount': gitRepoObj.get_issues().totalCount,
                        'contributersCount': gitRepoObj.get_contributors().totalCount
                    }
                    ,
                    identifier
                    ,
                    "",
                    "")
        except Exception as e:
            print(e)
            pass
        time.sleep(20)

if __name__ == "__main__":  # test
    print('uploading to mongo')
    c = CMC('')

    g = Git("")

    topCryptos = c.getLatestCryptocurrencyListings(10, "desc")

    try:
        for crypto in range(len(topCryptos.data)):
            try:
                gitRepo = c.getCryptoGitRepo(topCryptos.data[crypto]['symbol'])
                gitRepoObj = g.git.get_repo(gitRepo)
                if gitRepo and gitRepoObj:
                    print(gitRepoObj.get_commits().totalCount)
                    time.sleep(20)
            except:
                pass
    except Exception as e:
        print(e)
