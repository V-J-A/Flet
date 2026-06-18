from sqlalchemy import create_engine, Column, Integer, String, Text, Date, Time, DateTime, SmallInteger, Enum, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "mysql+mysqlconnector://root:joacoagon2009@localhost:3306/academia"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Especialidad(Base):
    __tablename__ = 'especialidad'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(10))
    nombre = Column(String(255))
    num_asignaturas = Column(Integer)
    titulo_oficial = Column(String(255))
    cursos = relationship("Curso", back_populates="especialidad")


class Curso(Base):
    __tablename__ = 'curso'
    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_curso = Column(Integer)
    id_especialidad = Column(Integer, ForeignKey('especialidad.id'))
    especialidad = relationship("Especialidad", back_populates="cursos")
    asignaturas = relationship("Asignatura", back_populates="curso")
    grupos = relationship("Grupo", back_populates="curso")


class Asignatura(Base):
    __tablename__ = 'asignatura'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String(20))
    nombre = Column(String(255))
    tipo = Column(Enum('TRONCAL', 'ESPECIALIZADA'))
    id_curso = Column(Integer, ForeignKey('curso.id'))
    curso = relationship("Curso", back_populates="asignaturas")


class Profesor(Base):
    __tablename__ = 'profesor'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(String(20))
    nombre = Column(String(255))
    apellidos = Column(String(255))
    domicilio = Column(String(255))
    nivel_estudios = Column(String(255))
    titulacion = Column(String(255))
    tipo = Column(Enum('TUTOR', 'ESPECIALISTA', 'AMBOS'))


class Grupo(Base):
    __tablename__ = 'grupo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(Enum('A', 'B', 'C'))
    id_curso = Column(Integer, ForeignKey('curso.id'))
    num_alumnos = Column(Integer)
    id_tutor = Column(Integer, ForeignKey('profesor.id'))
    curso = relationship("Curso", back_populates="grupos")
    tutor = relationship("Profesor")


class ProfesorEspecialista(Base):
    __tablename__ = 'profesor_especialista'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_profesor = Column(Integer, ForeignKey('profesor.id'))
    id_grupo = Column(Integer, ForeignKey('grupo.id'))
    id_asignatura = Column(Integer, ForeignKey('asignatura.id'))


class Alumno(Base):
    __tablename__ = 'alumno'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(String(20))
    nombre = Column(String(255))
    apellidos = Column(String(255))
    id_grupo = Column(Integer, ForeignKey('grupo.id'), nullable=True)


class HojaActividad(Base):
    __tablename__ = 'hoja_actividad'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_grupo = Column(Integer, ForeignKey('grupo.id'))
    fecha = Column(Date)
    id_profesor = Column(Integer, ForeignKey('profesor.id'))
    hora_inicio = Column(Time)
    hora_fin = Column(Time)


class FichaIndividual(Base):
    __tablename__ = 'ficha_individual'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_alumno = Column(Integer, ForeignKey('alumno.id'))
    mes = Column(Integer)
    anio = Column(SmallInteger)


class RegistroAsistencia(Base):
    __tablename__ = 'registro_asistencia'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_ficha = Column(Integer, ForeignKey('ficha_individual.id'))
    dia = Column(Integer)
    id_asignatura = Column(Integer, ForeignKey('asignatura.id'))
    id_profesor = Column(Integer, ForeignKey('profesor.id'))


class Candidato(Base):
    __tablename__ = 'candidato'
    id = Column(Integer, primary_key=True, autoincrement=True)
    dni = Column(String(20))
    nombre = Column(String(255))
    apellidos = Column(String(255))
    curriculum = Column(Text)
    tipo_deseado = Column(Enum('TUTOR', 'ESPECIALISTA', 'AMBOS'))
    materias = relationship("CandidatoMateria", back_populates="candidato")
    llamadas = relationship("Llamada", back_populates="candidato")
    entrevistas = relationship("Entrevista", back_populates="candidato")


class CandidatoMateria(Base):
    __tablename__ = 'candidato_materia'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_candidato = Column(Integer, ForeignKey('candidato.id'))
    id_asignatura = Column(Integer, ForeignKey('asignatura.id'))
    candidato = relationship("Candidato", back_populates="materias")


class Llamada(Base):
    __tablename__ = 'llamada'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_candidato = Column(Integer, ForeignKey('candidato.id'))
    fecha_hora = Column(DateTime)
    disposicion = Column(Enum('NO_LOCALIZADO', 'NO_INTERESADO', 'ENTREVISTA_CONCERTADA'))
    candidato = relationship("Candidato", back_populates="llamadas")


class Entrevista(Base):
    __tablename__ = 'entrevista'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_candidato = Column(Integer, ForeignKey('candidato.id'))
    id_llamada = Column(Integer, ForeignKey('llamada.id'))
    fecha = Column(Date)
    id_asignatura = Column(Integer, ForeignKey('asignatura.id'))
    valoracion = Column(String(255))
    id_comite = Column(Integer, ForeignKey('comite.id'))
    candidato = relationship("Candidato", back_populates="entrevistas")


class Comite(Base):
    __tablename__ = 'comite'
    id = Column(Integer, primary_key=True, autoincrement=True)
    anio = Column(SmallInteger)
    id_presidente = Column(Integer, ForeignKey('profesor.id'))
    id_secretario = Column(Integer, ForeignKey('profesor.id'))
    id_vocal = Column(Integer, ForeignKey('profesor.id'))


def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()
