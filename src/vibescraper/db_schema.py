from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime, Text, PickleType
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
import datetime

Base = declarative_base()

class Operation(Base):
    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)
    search_query = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    combined_summary = Column(Text, nullable=True)

    pages = relationship("Page", back_populates="operation",
                         cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Operation(id={self.id}, search_query='{self.search_query}')>"


class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    operation_id = Column(Integer, ForeignKey('operations.id'), nullable=False)
    url = Column(String, nullable=False)
    page_summary = Column(Text, nullable=True)

    operation = relationship("Operation", back_populates="pages")
    chunks = relationship("Chunk", back_populates="page",
                          cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Page(id={self.id}, url='{self.url}')>"


class Chunk(Base):
    __tablename__ = 'chunks'

    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('pages.id'), nullable=False)
    operation_id = Column(Integer, ForeignKey('operations.id'), nullable=False)
    rank = Column(Integer, nullable=True)
    chunk_text = Column(Text, nullable=False)
    # Store embedding as pickled data, not JSON
    embedding = Column(PickleType, nullable=True)
    similarity = Column(Float, nullable=True)

    page = relationship("Page", back_populates="chunks")

    def __repr__(self):
        return f"<Chunk(id={self.id}, rank={self.rank}, similarity={self.similarity})>"


class DBManager:
    def __init__(self, db_path='sqlite:///embeddings.db'):
        self.engine = create_engine(db_path, echo=False)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        Base.metadata.create_all(self.engine)

    def get_session(self):
        return self.Session()

    def close(self):
        self.engine.dispose()

    def create_operation(self, search_query):
        session = self.get_session()
        try:
            operation = Operation(search_query=search_query)
            session.add(operation)
            session.commit()
            operation_id = operation.id
            return operation_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_operation_summary(self, operation_id, summary):
        session = self.get_session()
        try:
            operation = session.query(Operation).get(operation_id)
            if operation:
                operation.combined_summary = summary
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def get_operation(self, operation_id):
        session = self.get_session()
        try:
            return session.query(Operation).get(operation_id)
        finally:
            session.close()

    def create_page(self, operation_id, url, page_summary=None):
        session = self.get_session()
        try:
            page = Page(operation_id=operation_id,
                        url=url, page_summary=page_summary)
            session.add(page)
            session.commit()
            page_id = page.id
            return page_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def update_page_summary(self, page_id, summary):
        session = self.get_session()
        try:
            page = session.query(Page).get(page_id)
            if page:
                page.page_summary = summary
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def create_chunk(self, page_id, operation_id, chunk_text, embedding=None, similarity=None, rank=None):
        session = self.get_session()
        try:
            chunk = Chunk(
                page_id=page_id,
                operation_id=operation_id,
                chunk_text=chunk_text,
                embedding=embedding,
                similarity=similarity,
                rank=rank
            )
            session.add(chunk)
            session.commit()
            chunk_id = chunk.id
            return chunk_id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
