import xmlrpc.client
import os
from sqlalchemy import create_engine, Column, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
Base = declarative_base()


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(String, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    is_company = Column(Boolean)
    has_message = Column(Boolean)
    is_blacklisted = Column(Boolean)
    activity_state = Column(String)
    activity_summary = Column(String)


def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def update_contacts():
    url = os.getenv("ODOO_URL")
    db = os.getenv("ODOO_DB")
    username = os.getenv("ODOO_USERNAME")
    password = os.getenv("ODOO_PASSWORD")

    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})

    if uid is False:
        raise Exception("Échec de l'authentification, mauvais identifiants")

    models = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")
    Session = init_db()
    contacts_data = models.execute_kw(
        db,
        uid,
        password,
        "res.partner",
        "search_read",
        [[]],
        {
            "fields": [
                "id",
                "name",
                "email",
                "phone",
                "is_company",
                "is_blacklisted",
                "activity_state",
                "activity_summary",
            ]
        },
    )

    session = Session()

    for partner in contacts_data:
        contact = session.query(Contact).filter_by(id=str(partner["id"])).first()

        if contact:
            contact.name = partner.get("name")
            contact.email = partner.get("email")
            contact.phone = partner.get("phone")
            contact.is_company = partner.get("is_company", False)
            contact.is_blacklisted = partner.get("is_blacklisted")
            contact.activity_state = partner.get("activity_state")
            contact.activity_summary = partner.get("activity_summary")
        else:
            new_contact = Contact(
                id=str(partner["id"]),
                name=partner.get("name"),
                email=partner.get("email"),
                phone=partner.get("phone"),
                is_company=partner.get("is_company", False),
                is_blacklisted=partner.get("is_blacklisted"),
                activity_state=partner.get("activity_state"),
                activity_summary=partner.get("activity_summary"),
            )
            session.add(new_contact)

    session.commit()
