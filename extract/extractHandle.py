import extract2 as extract

def main(postId, dbName, resp):
    client = MongoClient('localhost', 27017)
    db =  client.ahks_development
    # Databases for storing audio transcripts and text are differnt
    if dbName == "transcriptions":
            userInputData = db.transcriptions
    elif dbName == "documents":
            userInputData = db.documents

    # Databases for storing audio transcripts and text are differnt
    document = userInputData.find_one({'_id': ObjectId(postId)})
    
    if dbName == "transcriptions":
            transcriptionText = document['text']
    elif dbName == "documents":
            transcriptionText = document['data']
            
    #List of lines
    trans = transcriptionText.split("\n")
    
    respCode = resp.lower()[0]
    
    ret = None
    for sent in trans:
        ret = extract.deliverables(sent, respCode)
        if ret:
            print sent


if __name__ == "__main__":
    postId = sys.argv[1]
    dbName = sys.argv[2]
    resp = sys.argv[3] #(present | future)
    main(postId, dbName, resp)
    
    