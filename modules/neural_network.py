from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from modules.data_preparing import *


def calculate_similarity():
    library_books = prepare_library_data()

    new_books = prepare_new_data()

    model = SentenceTransformer('all-MiniLM-L6-v2')

    similarities = []

    existing_titles = [book[0] for book in library_books]
    existing_genres = [book[1] for book in library_books]
    existing_descriptions = [book[2] for book in library_books]
    existing_rankings = [book[3] for book in library_books]

    new_titles = [book[0] for book in new_books]
    new_genres = [book[1] for book in new_books]
    new_descriptions = [book[2] for book in new_books]

    existing_descriptions_combined = [title + " " + genre + " " + description for title, genre, description in
                                      zip(existing_titles, existing_genres, existing_descriptions)]
    new_descriptions_combined = [title + " " + genre + " " + description for title, genre, description in
                                 zip(new_titles, new_genres, new_descriptions)]

    all_descriptions = existing_descriptions_combined + new_descriptions_combined
    embeddings = model.encode(all_descriptions)

    similarity_matrix = cosine_similarity(embeddings[:len(library_books)], embeddings[len(library_books):])

    for idx, new_book in enumerate(new_books):
        similarity_scores = similarity_matrix[:, idx]

        weighted_rank = 0
        for i in range(len(similarity_scores)):
            weighted_rank += similarity_scores[i] * existing_rankings[i]

        similarities.append((new_book[0], weighted_rank))

    similarities.sort(key=lambda x: x[1], reverse=True)

    return similarities



