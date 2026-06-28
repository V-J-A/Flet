from sqlalchemy.orm import Session
from conexion import SessionLocal, Alumno, Grupo, Curso, Especialidad
from conexion import FichaIndividual, RegistroAsistencia, HojaActividad, Profesor


def listar_alumnos(db: Session):
    return db.query(Alumno).all()


def crear_alumno(db: Session, dni, nombre, apellidos, id_grupo):
    al = Alumno(dni=dni, nombre=nombre, apellidos=apellidos, id_grupo=id_grupo)
    db.add(al)
    db.commit()
    db.refresh(al)
    return al


def actualizar_alumno(db: Session, id_al, dni=None, nombre=None, apellidos=None, id_grupo=None):
    al = db.query(Alumno).get(id_al)
    if al:
        if dni: al.dni = dni
        if nombre: al.nombre = nombre
        if apellidos: al.apellidos = apellidos
        if id_grupo: al.id_grupo = id_grupo
        db.commit()
        db.refresh(al)
    return al


def eliminar_alumno(db: Session, id_al):
    al = db.query(Alumno).get(id_al)
    if al:
        db.delete(al)
        db.commit()
    return al


def listar_grupos(db: Session):
    return db.query(Grupo).all()


def crear_grupo(db: Session, codigo, id_curso, num_alumnos, id_tutor):
    g = Grupo(codigo=codigo, id_curso=id_curso, num_alumnos=num_alumnos, id_tutor=id_tutor)
    db.add(g)
    db.commit()
    db.refresh(g)
    return g


def listar_cursos(db: Session):
    return db.query(Curso).all()


def listar_especialidades(db: Session):
    return db.query(Especialidad).all()


def crear_ficha(db: Session, id_alumno, mes, anio):
    f = FichaIndividual(id_alumno=id_alumno, mes=mes, anio=anio)
    db.add(f)
    db.commit()
    db.refresh(f)
    return f


def registrar_asistencia(db: Session, id_ficha, dia, id_asignatura, id_profesor):
    r = RegistroAsistencia(id_ficha=id_ficha, dia=dia, id_asignatura=id_asignatura, id_profesor=id_profesor)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


def listar_hojas_actividad(db: Session):
    return db.query(HojaActividad).all()


def crear_hoja_actividad(db: Session, id_grupo, fecha, id_profesor, hora_inicio, hora_fin):
    h = HojaActividad(id_grupo=id_grupo, fecha=fecha, id_profesor=id_profesor,
                      hora_inicio=hora_inicio, hora_fin=hora_fin)
    db.add(h)
    db.commit()
    db.refresh(h)
    return h
