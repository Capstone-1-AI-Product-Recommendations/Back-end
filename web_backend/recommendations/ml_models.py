from keras.models import Sequential
from keras.layers import LSTM, Dense, Embedding
import numpy as np
from keras.models import Model
from keras.layers import Input, Embedding, Flatten, Dense, Concatenate
from textblob import TextBlob
from transformers import pipeline

class KnowledgeGraphEmbedding:
    def __init__(self, num_entities, num_relations, embedding_dim=50):
        self.num_entities = num_entities
        self.num_relations = num_relations
        self.embedding_dim = embedding_dim
        self.entity_embeddings = np.random.rand(num_entities, embedding_dim)
        self.relation_embeddings = np.random.rand(num_relations, embedding_dim)

    def train(self, triples, epochs=100, lr=0.01):
        for _ in range(epochs):
            for head, relation, tail in triples:
                h = self.entity_embeddings[head]
                r = self.relation_embeddings[relation]
                t = self.entity_embeddings[tail]
                loss = np.sum((h + r - t)**2)
                grad_h = 2 * (h + r - t)
                grad_r = grad_h
                grad_t = -grad_h
                self.entity_embeddings[head] -= lr * grad_h
                self.relation_embeddings[relation] -= lr * grad_r
                self.entity_embeddings[tail] -= lr * grad_t

    def predict(self, head, relation):
        scores = np.dot(self.entity_embeddings + self.relation_embeddings[relation], self.entity_embeddings.T)
        return np.argsort(scores[head])[-10:]


class ExplicitFactorModel:
    def __init__(self, product_embeddings):
        self.product_embeddings = product_embeddings
        # self.sentiment_analyzer = pipeline("sentiment-analysis")
        self.sentiment_analyzer = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
            revision="714eb0f"  # Phiên bản cụ thể
            )

    def analyze_sentiment(self, comment):
        result = self.sentiment_analyzer(comment)
        return result[0]['score'] if result else 0

    def recommend(self, user_id, comments, top_n=10):
        sentiment_scores = [self.analyze_sentiment(comment) for comment in comments]
        recommended_indices = np.argsort(sentiment_scores)[-top_n:]
        return recommended_indices


class LSTMRecommender:
    def __init__(self, num_products, embedding_dim=50, lstm_units=50):
        self.num_products = num_products
        self.embedding_dim = embedding_dim
        self.lstm_units = lstm_units
        self.model = self._build_model()

    def _build_model(self):
        # Product sequence input
        product_input = Input(shape=(10,))
        product_embedding = Embedding(input_dim=self.num_products, output_dim=self.embedding_dim)(product_input)
        
        # Search query vector (as additional input)
        search_input = Input(shape=(50,))  # Assuming search_query is vectorized to size 50
        
        # LSTM layer for product sequence
        lstm_out = LSTM(self.lstm_units, activation='tanh')(product_embedding)

        # Concatenate LSTM output with search query
        combined_input = Concatenate()([lstm_out, search_input])

        # Dense layers for final prediction
        dense_1 = Dense(128, activation='relu')(combined_input)
        output = Dense(self.num_products, activation='softmax')(dense_1)

        model = Model(inputs=[product_input, search_input], outputs=output)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def train(self, X, y, search_vectors, epochs=5, batch_size=32):
        self.model.fit([X, search_vectors], y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict_next_product(self, sequence, search_vector):
        prediction = self.model.predict([np.array([sequence]), np.array([search_vector])])
        return np.argsort(prediction[0])[-10:]


class NeuralCollaborativeFiltering:
    def __init__(self, num_users, num_products, latent_dim=8):
        self.num_users = num_users
        self.num_products = num_products
        self.latent_dim = latent_dim
        self.model = self._build_model()

    def _build_model(self):
        user_input = Input(shape=(1,))
        product_input = Input(shape=(1,))

        user_embedding = Embedding(self.num_users, self.latent_dim)(user_input)
        product_embedding = Embedding(self.num_products, self.latent_dim)(product_input)

        user_flat = Flatten()(user_embedding)
        product_flat = Flatten()(product_embedding)

        concatenated = Concatenate()([user_flat, product_flat])
        dense_1 = Dense(64, activation='relu')(concatenated)
        dense_2 = Dense(32, activation='relu')(dense_1)
        output = Dense(1, activation='sigmoid')(dense_2)

        model = Model(inputs=[user_input, product_input], outputs=output)
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def train(self, X, y, behavior_weights=None, epochs=5, batch_size=32):
        if behavior_weights is not None:
            y = y * behavior_weights
        self.model.fit([X[:, 0], X[:, 1]], y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, user_id, product_id):
        if user_id >= self.num_users or product_id >= self.num_products:
            return 0  # Return a default score if indices are out of bounds
        return self.model.predict([np.array([user_id]), np.array([product_id])])[0][0]
