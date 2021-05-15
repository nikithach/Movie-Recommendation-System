import pandas as pa
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import operator

ratingDataset = pa.read_csv('ratings.csv')
movieDataset = pa.read_csv('movies.csv')
tagsDataset = pa.read_csv('tags.csv')
ratingDataset = ratingDataset.reindex(columns=["movieId","rating"])
movieTitleDataset = movieDataset.reindex(columns=["movieId","title"])
movieTagDataset = pa.merge(movieTitleDataset,tagsDataset,on='movieId')
x=pa.merge(ratingDataset,movieTitleDataset,on='movieId')
x=x.reindex(columns=["movieId","title"])
movieNameRatingDataset=pa.merge(ratingDataset,movieTitleDataset,on='movieId')
print(ratingDataset.isnull().sum())

wcss=[]
for i in range(1,11):
    kmeans=KMeans(n_clusters=i,init='k-means++',n_init=10,max_iter=300,random_state=0)
    kmeans.fit(ratingDataset)
    wcss.append(kmeans.inertia_)
plt.plot(range(1,11),wcss)
plt.title('Finding optimal k')
plt.xlabel('no.of clusters')
plt.ylabel('wcss score')
plt.show()

def kmeansClustering():
    kmeansClusterObject=KMeans(n_clusters=6)
    kmeansClusterObject.fit(ratingDataset)
    ratingDataset['clusterName']=kmeansClusterObject.labels_
    e=[]
    def groupFun(movieGroup):
        a = pa.DataFrame(movieGroup)
        b = pa.DataFrame(a['clusterName'].value_counts())
        d = a.index
        c = [a['movieId'][d[0]],int(b.idxmax())]
        e.append(c)
    ratingDataset.groupby('movieId').apply(lambda x:groupFun(x))
    e=e[1:]
    ex=pa.DataFrame(e)
    ex.rename(columns = {0:'movieId',1:'clusterName'},inplace=True)
    ex=pa.merge(ex,movieTitleDataset,on='movieId')
    return ex

def findSimilarRatingMovies(movieName):    
    ex=kmeansClustering()
    clusterInfo=ex['clusterName'][ex.title==movieName]
    movieNames = ex['title'][ex.clusterName==int(clusterInfo)].sample(100)
    filteredMovieNames=[]
    for i in movieNames:
        if len(x[x['title']==i])>15:
            filteredMovieNames.append(i)
    return filteredMovieNames

def findSimilarGenerMovies(movieName):
    movieRatingList = findSimilarRatingMovies(movieName)
    b=movieDataset[movieDataset.title==movieName].genres.to_string()
    b=b.split()
    b=b[1].split('|')    
    d=dict()
    for i in movieRatingList:
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
for movie in similarRatedMovies:
    print(count,")",movie)
    count=count+1

print(":::Similar movies:::")
count=1
for movie in similarGenerMovies:
    print(count,")",movie)
    count=count+1

print(":::Similar movies:::")
count=1
for movie in similarTagList:
    print(count,")",movie)
    count=count+1