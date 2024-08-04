# The purpose of this file is to manage schema for the graph
import pandas as pd
from docutils.core import Publisher

import import_data
import configuration
from neomodel import (StructuredNode)
from neomodel import (RelationshipFrom, RelationshipTo)
from neomodel import (StringProperty, IntegerProperty)
from neomodel import (install_all_labels, config)

config.DATABASE_URL = 'bolt://neo4j:neo4j@localhost:7687'
config.DATABASE_NAME = 'gai'

class Book(StructuredNode):
	title = StringProperty(unique_index=True, required=True)
	isbn = StringProperty(unique_index=True)
	isbn13 = StringProperty(unique_index=True)
	publication_year = IntegerProperty()
	summary = StringProperty()
	topics = RelationshipTo('Topics', 'EXAMPLE_OF')
	genres = RelationshipFrom('Genre', 'EXAMPLE_OF')
	authors = RelationshipFrom('Author', 'AUTHORED')
	additional_authors = RelationshipFrom('Author', 'AUTHORED')  # TODO create additional authors
	publisher = RelationshipTo('Publisher', 'PUBLISHED')


class Author(StructuredNode):
	name = StringProperty(unique_index=True, required=True)
	books = RelationshipTo('Book', 'AUTHORED')
	writer_of = RelationshipTo('Genres', 'INTERESTED_IN')
	interests = RelationshipTo('Topics', 'INTERESTED_IN')
	publisher = RelationshipFrom('Publisher', 'PUBLISHED')

	class Publisher(StructuredNode):
		name = StringProperty(unique_index=True)
		books = RelationshipFrom(Book, 'PUBLISHED')
		authors = RelationshipTo('Author', 'Published')


class Genre(StructuredNode):
	name = StringProperty(unique_index=True)
	books = RelationshipTo(Book, 'EXAMPLE_OF')
	authors = RelationshipFrom(Author, 'INTERESTED_IN')
	topics = RelationshipTo('Topics', 'EXAMPLE_OF')


class Topics(StructuredNode):
	name = StringProperty(unique_index=True)
	examples = RelationshipTo(Book, 'EXAMPLE_OF')
	authors = RelationshipFrom(Author, 'INTERESTED_IN')
	genres = RelationshipFrom(Genre, 'EXAMPLE_OF')


class HANDLER:
	def __init__(self):
		data_to_import = import_data.CONTAINER.resource_dataframe
		pd.DataFrame(data_to_import)

	def pass_to_nodes(self, data_to_import):
		for index, row in data_to_import.iterrows():
			book = Book(
				title=row['titles'],
				isbn=row['isbn'],
				isbn13=row['isbn13'],
				publication_year=row['publication_years'],
				summary=row['summaries']
			).save()

			author = Author(name=row['authors']).save()
			publisher = Publisher(name=row['publisher']).save()
			genre = Genre(name=row['genres']).save()
			topic = Topics(name=row['topics']).save()

			author.books.connect(book)
			publisher.books.connect(book)
			book.genres.connect(genre)
			book.topics.connect(topic)
			author.writer_of.connect(genre)
			author.interests.connect(topic)
			genre.authors.connect(author)
			topic.authors.connect(author)
			topic.genres.connect(genre)


install_all_labels()
