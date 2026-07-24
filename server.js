const express = require('express');
const cors = require('cors');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(express.json());

app.use(express.static(__dirname));

// Initialize SQLite database
const db = new sqlite3.Database('./database.sqlite', (err) => {
    if (err) {
        console.error('Error opening database', err.message);
    } else {
        console.log('Connected to the SQLite database.');
        
        // Create tables if they don't exist
        db.serialize(() => {
            db.run(`
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    email TEXT,
                    password TEXT
                )
            `);
            // Add email column if it doesn't exist (migration for existing DBs)
            db.run(`ALTER TABLE users ADD COLUMN email TEXT`, () => {});
            
            db.run(`
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    search_term TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            `);
            
            db.run(`
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    recipe_name TEXT,
                    recipe_id INTEGER,
                    image_url TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            `);
        });
    }
});

// API Endpoints

// Register
app.post('/api/register', (req, res) => {
    const { username, email, password } = req.body;
    if (!username || !password) {
        return res.status(400).json({ error: 'Username and password are required' });
    }
    
    db.run('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', [username, email || null, password], function(err) {
        if (err) {
            if (err.message.includes('UNIQUE constraint failed')) {
                return res.status(400).json({ error: 'Username already exists' });
            }
            return res.status(500).json({ error: err.message });
        }
        res.status(201).json({ id: this.lastID, username, email: email || null });
    });
});

// Login
app.post('/api/login', (req, res) => {
    const { username, password } = req.body;
    
    db.get('SELECT id, username, email FROM users WHERE username = ? AND password = ?', [username, password], (err, row) => {
        if (err) {
            return res.status(500).json({ error: err.message });
        }
        if (!row) {
            return res.status(401).json({ error: 'Invalid credentials' });
        }
        res.json(row);
    });
});

// Save search history
app.post('/api/history', (req, res) => {
    const { user_id, search_term } = req.body;
    if (!user_id || !search_term) return res.status(400).json({ error: 'Missing data' });
    
    db.run('INSERT INTO history (user_id, search_term) VALUES (?, ?)', [user_id, search_term], function(err) {
        if (err) return res.status(500).json({ error: err.message });
        res.status(201).json({ id: this.lastID, search_term });
    });
});

// Save favorite recipe
app.post('/api/favorites', (req, res) => {
    const { user_id, recipe_name, recipe_id, image_url } = req.body;
    if (!user_id || !recipe_name) return res.status(400).json({ error: 'Missing data' });
    
    // Check if already favorited to prevent duplicates
    db.get('SELECT id FROM favorites WHERE user_id = ? AND recipe_name = ?', [user_id, recipe_name], (err, row) => {
        if (err) return res.status(500).json({ error: err.message });
        if (row) return res.status(400).json({ error: 'Recipe already in favorites' });
        
        db.run('INSERT INTO favorites (user_id, recipe_name, recipe_id, image_url) VALUES (?, ?, ?, ?)', 
            [user_id, recipe_name, recipe_id || null, image_url || null], 
            function(err) {
                if (err) return res.status(500).json({ error: err.message });
                res.status(201).json({ id: this.lastID, recipe_name });
            }
        );
    });
});

// Delete from favorite
app.delete('/api/favorites/:id', (req, res) => {
    const favorite_id = req.params.id;
    const user_id = req.query.user_id;

    if(!favorite_id || !user_id) return res.status(400).json({ error: 'Missing data' });

    db.run('DELETE FROM favorites WHERE id = ? AND user_id = ?', [favorite_id, user_id], function(err){
        if (err) return res.status(500).json({ error: err.message });
        res.json({ message: 'Deleted' });
    })
})

// Get user profile (history and favorites)
app.get('/api/user/:id', (req, res) => {
    const user_id = req.params.id;
    
    const responseData = { history: [], favorites: [], email: null };
    
    db.get('SELECT email FROM users WHERE id = ?', [user_id], (err, userRow) => {
        if (!err && userRow) responseData.email = userRow.email;

        db.all('SELECT * FROM history WHERE user_id = ? ORDER BY created_at DESC LIMIT 20', [user_id], (err, historyRows) => {
            if (err) return res.status(500).json({ error: err.message });
            responseData.history = historyRows;
            
            db.all('SELECT * FROM favorites WHERE user_id = ? ORDER BY created_at DESC', [user_id], (err, favoritesRows) => {
                if (err) return res.status(500).json({ error: err.message });
                responseData.favorites = favoritesRows;
                res.json(responseData);
            });
        });
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`Server running at http://localhost:${PORT}`);
});
