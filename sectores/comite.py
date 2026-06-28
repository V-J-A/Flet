from sqlalchemy.orm import Session
from conexion import SessionLocal, Comite, Profesor


def listar_comites(db: Session):
    return db.query(Comite).all()


def crear_comite(db: Session, anio, id_presidente, id_secretario, id_vocal):
    c = Comite(anio=anio, id_presidente=id_presidente,
               id_secretario=id_secretario, id_vocal=id_vocal)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def actualizar_comite(db: Session, id_c, anio=None, id_presidente=None,
                      id_secretario=None, id_vocal=None):
    c = db.query(Comite).get(id_c)
    if c:
        if anio: c.anio = anio
        if id_presidente: c.id_presidente = id_presidente
        if id_secretario: c.id_secretario = id_secretario
        if id_vocal: c.id_vocal = id_vocal
        db.commit()
        db.refresh(c)
    return c


def eliminar_comite(db: Session, id_c):
    c = db.query(Comite).get(id_c)
    if c:
        db.delete(c)
        db.commit()
    return c


def listar_profesores(db: Session):
    return db.query(Profesor).all()
