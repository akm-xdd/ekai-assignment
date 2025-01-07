from .db_manager import DBManager

def display_result(result):
    """Display search result in a formatted way"""
    if result:
        print("\nFound Document:")
        print("-" * 50)
        print(f"Source: {result['document_metadata']['source']}")
        print(f"Date: {result['document_metadata']['date']}")
        print(f"Version: {result['document_metadata']['version']}")
        print(f"Security Level: {result['document_metadata']['security']}")
        print(f"\nTotal Chunks: {result['total_chunks']}")
        
        print("\nDocument Content:")
        print("-" * 50)
        for chunk in result['chunks']:
            print(f"\nChunk {chunk['metadata']['chunk_id'] + 1} of {chunk['metadata']['total_chunks']}:")
            print(chunk['content'])
            print("-" * 30)
    else:
        print("\nNo matching documents found.")

def view_all_documents(db):
    """Display all documents stored in the database"""
    results = db.view_all_documents()
    
    if not results:
        print("\nNo documents found in the database.")
        return
        
    print("\nAll Stored Documents:")
    print("-" * 50)
    for i, doc in enumerate(results, 1):
        print(f"\nDocument {i}:")
        print(f"Source: {doc['metadata']['source']}")
        print(f"Content: {doc['content']}")
        print(f"Date: {doc['metadata']['date']}")
        print(f"Version: {doc['metadata']['version']}")
        print(f"Security Level: {doc['metadata']['security']}")
        print(f"Chunk: {doc['metadata']['chunk_id'] + 1} of {doc['metadata']['total_chunks']}")
        print("-" * 50)

def main():
    print("Initializing PDF Document Manager...")
    try:
        db = DBManager()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        return

    while True:
        print("\nPDF Document Manager")
        print("-" * 50)
        print("1. Store new documents from PDFs")
        print("2. Search by date")
        print("3. Search by date and security level")
        print("4. View all stored documents")
        print("5. Clear database")
        print("6. Exit")
        
        choice = input("\nEnter your choice (1-6): ")

        if choice == "1":
            print("\nProcessing and storing documents...")
            db.store_initial_documents()
                
        elif choice == "2":
            date = input("Enter date (YYYY-MM-DD): ")
            try:
                result = db.find_closest_date_documents(date)
                display_result(result)
            except ValueError as e:
                print(f"Error: {e}")
                print("Please enter date in YYYY-MM-DD format")
                
        elif choice == "3":
            date = input("Enter date (YYYY-MM-DD): ")
            security = input("Enter security level (Public/Confidential/Restricted/Top Secret): ")
            security = security.lower().capitalize()
            try:
                result = db.search_with_security(date, security)
                display_result(result)
            except ValueError as e:
                print(f"Error: {e}")
                
        elif choice == "4":
            view_all_documents(db)
            
        elif choice == "5":
            confirm = input("Are you sure you want to clear the database? (y/n): ")
            if confirm.lower() == 'y':
                db.clear_database()
            
        elif choice == "6":
            print("\nThank you for using PDF Document Manager!")
            break
            
        else:
            print("\nInvalid choice. Please try again.")

if __name__ == "__main__":
    main()