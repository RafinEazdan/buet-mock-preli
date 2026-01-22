from fastapi import Depends, FastAPI

from app.database import get_db

app = FastAPI()

# Pydantic models for request bodies


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check(db=Depends(get_db)):
    db.execute("SELECT 1")
    return {"status": "ok"}

@app.get("/companies")
def get_companies(db=Depends(get_db)):
    cursor = db.execute("SELECT * FROM companies ORDER BY company_id")
    companies = cursor.fetchall()
    return {"companies": companies}

@app.post("/companies")
def create_company(company: CompanyCreate, db=Depends(get_db)):
    cursor = db.execute(
        "INSERT INTO companies (name, industry) VALUES (%s, %s) RETURNING *",
        (company.name, company.industry)
    )
    new_company = cursor.fetchone()
    return {"message": "Company created successfully", "company": new_company}

@app.get("/contacts")
def get_contacts(db=Depends(get_db)):
    cursor = db.execute("""
        SELECT 
            c.contact_id,
            c.first_name,
            c.last_name,
            c.email,
            c.phone,
            co.name as company_name
        FROM contacts c
        LEFT JOIN companies co ON c.company_id = co.company_id
        ORDER BY c.contact_id
    """)
    contacts = cursor.fetchall()
    return {"contacts": contacts}

@app.post("/contacts")
def create_contact(contact: ContactCreate, db=Depends(get_db)):
    cursor = db.execute(
        """INSERT INTO contacts (first_name, last_name, email, phone, company_id) 
           VALUES (%s, %s, %s, %s, %s) RETURNING *""",
        (contact.first_name, contact.last_name, contact.email, contact.phone, contact.company_id)
    )
    new_contact = cursor.fetchone()
    return {"message": "Contact created successfully", "contact": new_contact}

@app.get("/companies/{company_id}")
def get_company(company_id: int, db=Depends(get_db)):
    cursor = db.execute(
        "SELECT * FROM companies WHERE company_id = %s",
        (company_id,)
    )
    company = cursor.fetchone()
    if not company:
        return {"error": "Company not found"}
    
    # Get contacts for this company
    cursor = db.execute(
        "SELECT * FROM contacts WHERE company_id = %s",
        (company_id,)
    )
    contacts = cursor.fetchall()
    
    return {
        "company": company,
        "contacts": contacts
    }


