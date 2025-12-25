# Working with MongoDB via Voice Commands

## 🎉 New Features

Now you can manage MongoDB through voice commands! All basic operations with databases, collections, and documents are supported.

## 🚀 Quick Start

### 1. Make Sure MongoDB is Running

```bash
# Check that MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# If not running, start it (depends on your installation)
# brew services start mongodb-community  # for Homebrew
```

### 2. Configure Connection String (Optional)

By default, `mongodb://localhost:27017` is used. If you need to change it:

```bash
export MONGODB_URI="mongodb://your-connection-string"
```

### 3. Rebuild MCP Server

```bash
npm run build
```

## 📝 Voice Command Examples

### Opening MongoDB Compass

```
"Open MongoDB Compass"
```

### Working with Databases

```
"Create database test"
"Show list of databases"
```

### Working with Collections

```
"Create collection users in database test"
"Show collections in database test"
"Delete collection users from database test"
```

### Working with Documents

```
"Add document {"name": "John", "age": 30} to collection users in database test"
"Find all documents in collection users in database test"
"Find documents with name John in collection users in database test"
"Delete document with name John from collection users in database test"
```

## 🎤 Complete Usage Example

```bash
python3 voice_client.py
```

Then speak commands:

1. **"Open MongoDB Compass"** - opens MongoDB Compass
2. **"Create database testdb"** - creates database
3. **"Create collection users in database testdb"** - creates collection
4. **"Add document {"name": "Alice", "email": "alice@example.com"} to collection users in database testdb"**
5. **"Find all documents in collection users in database testdb"** - shows all documents
6. **"Delete document with name Alice from collection users in database testdb"**

## 📋 Available MongoDB Tools

### Databases

- **`mongodb_create_database`** - Create database
- **`mongodb_list_databases`** - List all databases

### Collections

- **`mongodb_create_collection`** - Create collection
- **`mongodb_list_collections`** - List collections in database
- **`mongodb_delete_collection`** - Delete collection

### Documents

- **`mongodb_insert_document`** - Insert document
- **`mongodb_find_documents`** - Find documents (with filter)
- **`mongodb_delete_document`** - Delete document(s) by filter

## 🔧 JSON Examples for Documents

When adding documents, use JSON format:

```
{"name": "John", "age": 30, "city": "Moscow"}
{"title": "Test", "value": 100, "active": true}
{"_id": "custom-id", "data": "some data"}
```

## ⚠️ Important Notes

1. **Connection String**: Default is `mongodb://localhost:27017`. For MongoDB Atlas or other servers, use the `MONGODB_URI` environment variable.

2. **JSON Format**: When using voice commands, Ollama automatically converts your speech to JSON. For complex structures, multiple attempts may be needed.

3. **Security**: Make sure MongoDB is properly configured from a security perspective, especially if accessible externally.

4. **Filters**: When searching and deleting documents, use JSON filters:
   - All documents: `{}` (empty object)
   - By field: `{"name": "John"}`
   - With conditions: `{"age": {"$gt": 18}}`

## 🐛 Troubleshooting

### Connection Error to MongoDB

**Solution:**
```bash
# Check that MongoDB is running
mongosh --eval "db.adminCommand('ping')"

# Check connection string
echo $MONGODB_URI
```

### Database Not Created

MongoDB creates databases automatically when first data is added. The `mongodb_create_database` tool creates a temporary collection to initialize the database.

### Command Not Recognized

Use simpler formulations:
- ✅ "Create database test"
- ✅ "Add to collection users document {"name": "John"}"
- ❌ "I need to create a database named test and add a collection there"

## 📚 Additional Resources

- [MongoDB Documentation](https://www.mongodb.com/docs/)
- [MongoDB Node.js Driver](https://www.mongodb.com/docs/drivers/node/current/)
