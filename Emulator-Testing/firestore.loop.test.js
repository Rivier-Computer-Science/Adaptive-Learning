const fs = require("fs");
const { initializeTestEnvironment } = require("@firebase/rules-unit-testing");
const { getAllUsers } = require("./fetchUsers");

// Dynamically load projectId from .firebaserc
const FIREBASERC = JSON.parse(fs.readFileSync(".firebaserc", "utf8"));
const PROJECT_ID = FIREBASERC.projects.default;
const RULES_FILE = "firestore.rules";

async function run() {
  const users = await getAllUsers();

  if (users.length < 2) {
    console.error(" Need at least 2 users in Auth Emulator to test properly.");
    return;
  }

  const testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: {
      host: "localhost",
      port: 8080,
      rules: fs.readFileSync(RULES_FILE, "utf8")
    }
  });

  const anon = testEnv.unauthenticatedContext();
  const anonDb = anon.firestore();

  console.log(`\nFound ${users.length} users in Emulator`);
  console.log(users.map(u => `${u.email} (${u.uid})`).join("\n"));

  for (const user of users) {
    const { uid, email } = user;
    const userCtx = testEnv.authenticatedContext(uid);
    const userDb = userCtx.firestore();

    // Should write to their own path
    try {
      await userDb.collection("users").doc(uid).collection("sessions").add({ test: "own path" });
      console.log(`${email} can write to /users/${uid} (expected)`);
    } catch {
      console.log(`${email} was blocked from own path (unexpected)`);
    }

    // Should NOT write to other users' paths
    for (const other of users) {
      if (other.uid === uid) continue;

      try {
        await userDb.collection("users").doc(other.uid).collection("sessions").add({ test: "wrong path" });
        console.log(`${email} wrote to /users/${other.uid} — SHOULD BE BLOCKED`);
      } catch {
        console.log(`${email} was blocked from /users/${other.uid} (expected)`);
      }
    }
  }

  // Anonymous test
  try {
    const victim = users[0];
    await anonDb.collection("users").doc(victim.uid).collection("sessions").add({ test: "anon access" });
    console.log(`Anonymous write succeeded for ${victim.uid} — SHOULD BE BLOCKED`);
  } catch {
    console.log(`Anonymous write was blocked (expected)`);
  }

  await testEnv.cleanup();
}

run();
