const admin = require("firebase-admin");

// IMPORTANT: This line ensures the Admin SDK talks to the local emulator
process.env.FIREBASE_AUTH_EMULATOR_HOST = "localhost:9099";

// This projectId MUST match your emulator’s project (shown in Emulator UI)
admin.initializeApp({
  projectId: "adaptive-learning-rivier"  // <-- update if yours is different
});

async function getAllUsers() {
  try {
    const result = await admin.auth().listUsers();
    return result.users.map(u => ({
      uid: u.uid,
      email: u.email
    }));
  } catch (e) {
    console.error("Failed to fetch users:", e.message);
    return [];
  }
}

module.exports = { getAllUsers };
