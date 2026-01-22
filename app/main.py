from fastapi import Depends, FastAPI, HTTPException
from app.database import get_db
from app.schemas import CompanyCreate, ContactCreate, ParseRequest, ParseResponse
from app.llm import extract_contact_info

app = FastAPI()


@app.post("/parse", response_model=ParseResponse)
def parse_contact(request: ParseRequest, db=Depends(get_db)):
    """
    Parse contact information from natural language text using LLM
    and validate against the database.
    """
    try:
        # Extract contact info using LLM
        extracted = extract_contact_info(request.text)
        
        name = extracted.get("name", "")
        email = extracted.get("email")
        phone = extracted.get("phone")
        
        # Search for contact in database by email or phone
        found_in_database = False
        company_name = None
        
        if email or phone:
            query = """
                SELECT 
                    c.first_name || ' ' || c.last_name as full_name,
                    c.email,
                    c.phone,
                    co.name as company_name
                FROM contacts c
                LEFT JOIN companies co ON c.company_id = co.company_id
                WHERE 1=0
            """
            params = []
            
            if email:
                query += " OR LOWER(c.email) = LOWER(%s)"
                params.append(email)
            
            if phone:
                query += " OR c.phone = %s"
                params.append(phone)
            
            cursor = db.execute(query, tuple(params))
            result = cursor.fetchone()
            
            if result:
                found_in_database = True
                company_name = result.get("company_name")
                # Use database values when contact is found
                if result.get("full_name"):
                    name = result["full_name"]
                if result.get("email"):
                    email = result["email"]
                if result.get("phone"):
                    phone = result["phone"]
        
        return ParseResponse(
            name=name,
            email=email,
            phone=phone,
            found_in_database=found_in_database,
            company=company_name
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.get("/")
async def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check(db=Depends(get_db)):
    db.execute("SELECT 1")
    return {"status": "ok", "database": "connected"}

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


