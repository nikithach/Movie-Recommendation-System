import pandas as pa
import operator

ratingDataset = pa.read_csv('ratings.csv')
movieDataset = pa.read_csv('movies.csv')
tagsDataset = pa.read_csv('tags.csv')
ratingDataset = ratingDataset.reindex(columns=["userId","movieId","rating"])
movieDataset = movieDataset.reindex(columns=["movieId","title","genres"])
movieTitleDataset = movieDataset.reindex(columns=["movieId","title"])
tagsDataset = tagsDataset.reindex(columns = ["movieId","tag"])

print(ratingDataset.isnull().sum())
print(movieDataset.isnull().sum())

mergedData = pa.merge(ratingDataset,movieDataset,on='movieId')
movieTagDataset = pa.merge(movieTitleDataset,tagsDataset,on='movieId')
print(mergedData.isnull().sum())
avgRatingCountDataset = pa.DataFrame(mergedData.groupby('title')['rating'].mean())
avgRatingCountDataset['count'] = pa.DataFrame(mergedData.groupby('title')['rating'].count())
avgRatingCountDataset = avgRatingCountDataset.sort_values('count',ascending=False)
movieRatingMatrix = mergedData.pivot_table(index='userId',columns='title',values='rating')

def findSimilarRatingMovies(movieName):
    movieNameUserRatings = movieRatingMatrix[movieName]
    movieNameCorrWithOtherMovies = movieRatingMatrix.corrwith(movieNameUserRatings)
    movieCorr = pa.DataFrame(movieNameCorrWithOtherMovies,columns=['similarity'])
    movieCorr.dropna(inplace=True)
    movieCorrWithMovieCount = movieCorr.join(avgRatingCountDataset['count'])
    movieCorrWithMovieCount = movieCorrWithMovieCount[movieCorrWithMovieCount['count']>15].sort_values('similarity',ascending=False)
    movieCorrWithMovieCount = movieCorrWithMovieCount[movieCorrWithMovieCount.index!=movieName]
    return movieCorrWithMovieCount.head(30)

def findSimilarGenerMovies(movieName):
    movieRatingList = findSimilarRatingMovies(movieName)
    b=movieDataset[movieDataset.title==movieName].genres.to_string()
    b=b.split()
    b=b[1].split('|')    
    d=dict()
    for i,j in movieRatingList.iterrows():
        x=movieDataset[movieDataset.title==i].genres.to_string()
        data=x.split()
        lists=data[1].split('|')
        c=list(set(b).intersection(lists))
        d[i]=len(c)
    sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
    movieSortedGenerList = list()
    count = 0
    for entry in sorted_d:
        if count<10:
            count=count+1
            movieSortedGenerList.append(entry[0])
        else:
            break
    return movieSortedGenerList

def findSimilarTaggedMovies(movieName):
    movieGenerList = findSimilarGenerMovies(movieName)
    movieNameTag = movieTagDataset[movieTagDataset.title==movieName].tag.tolist()
    d=dict()
    for i in movieGenerList:
        x = movieTagDataset[movieTagDataset.title==i].tag.tolist()
        c=list(set(movieNameTag).intersection(x))
        d[i]=len(c)  
    sorted_d = sorted(d.items(), key=operator.itemgetter(1), reverse=True)
    movieSortedTagList = list()
    for entry in sorted_d:
        if entry[1]>0:
            movieSortedTagList.append(entry[0])   
    return movieSortedTagList   

movieName=input("enter movie name:::::")

similarRatedMovies = findSimilarRatingMovies(movieName)
similarGenerMovies = findSimilarGenerMovies(movieName)
similarTagList=findSimilarTaggedMovies(movieName)

print(":::Similar movies:::")
count=1
for movie in similarRatedMovies.iterrows():
    print(count,")",movie[0])
    count=count+1
    
print("\n:::Similar movies:::Based on Genre")
count=1
for movie in similarGenerMovies:
    print(count,")",movie)
    count=count+1

print("\n:::Similar movies:::Based on Tags")
count=1
for movie in similarTagList:
    print(count,")",movie)
    count=count+1