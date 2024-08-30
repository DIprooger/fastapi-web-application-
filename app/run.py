from conf import engine, Base
import uvicorn


Base.metadata.create_all(bind=engine)

print("Tables created successfully.")

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
