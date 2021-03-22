import argparse, firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

def init_firestore(project_name):

    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred, {
      'projectId': project_name,
    })

    db = firestore.client()

    doc_ref = db.collection(u'ok').document(u'test-data')
    doc_ref.set({
        u'init': u'done!'
    })

    print("Firestore write done")

if __name__ == "__main__":

    # Project ID is passed at run-time
    parser = argparse.ArgumentParser()
    parser.add_argument("--project_id", help="Google Cloud project id")
    args = parser.parse_args()
    project_id = args.project_id
    print(f"starting to init smaregi starter kit in Google Cloud project:{project_id}")

    # init Firestore instance
    init_firestore(project_id)