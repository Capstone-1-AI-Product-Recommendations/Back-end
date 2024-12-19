from keras.models import Sequential
from keras.layers import LSTM, Dense, Embedding
import numpy as np
from keras.models import Model
from keras.layers import Input, Embedding, Flatten, Dense, Concatenate
from textblob import TextBlob

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

                # Loss: Distance between (h + r) and t
                loss = np.sum((h + r - t)**2)
                grad_h = 2 * (h + r - t)
                grad_r = grad_h
                grad_t = -grad_h

                # Update embeddings
                self.entity_embeddings[head] -= lr * grad_h
                self.relation_embeddings[relation] -= lr * grad_r
                self.entity_embeddings[tail] -= lr * grad_t

    def predict(self, head, relation):
        scores = np.dot(self.entity_embeddings + self.relation_embeddings[relation], self.entity_embeddings.T)
        return np.argsort(scores[head])[-10:]

class ExplicitFactorModel:
    def __init__(self, product_embeddings):
        self.product_embeddings = product_embeddings

    def analyze_sentiment(self, comment):
        blob = TextBlob(comment)
        return blob.sentiment.polarity

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
        model = Sequential()
        model.add(Embedding(input_dim=self.num_products, output_dim=self.embedding_dim, input_length=10))
        model.add(LSTM(self.lstm_units, activation='tanh'))
        model.add(Dense(self.num_products, activation='softmax'))
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
        return model

    def train(self, X, y, epochs=5, batch_size=32):
        self.model.fit(X, y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict_next_product(self, sequence):
        prediction = self.model.predict(np.array([sequence]))
        return np.argsort(prediction[0])[-10:]  # Top 10 recommendations

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

    def train(self, X, y, epochs=5, batch_size=32):
        self.model.fit([X[:, 0], X[:, 1]], y, epochs=epochs, batch_size=batch_size, verbose=1)

    def predict(self, user_id, product_id):
        if user_id >= self.num_users or product_id >= self.num_products:
            return 0  # Return a default score if indices are out of bounds
        return self.model.predict([np.array([user_id]), np.array([product_id])])[0][0]
