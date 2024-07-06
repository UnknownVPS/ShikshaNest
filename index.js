const express = require('express');
const { google } = require('googleapis');
const bodyParser = require('body-parser');
const { v4: uuidv4 } = require('uuid');

const app = express();
app.use(bodyParser.json());

const CLIENT_ID = process.env.CLIENT_ID;
const CLIENT_SECRET = process.env.CLIENT_SECRET;
const REDIRECT_URI = process.env.REDIRECT_URI;

const oauth2Client = new google.auth.OAuth2(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI);

const SCOPES = ['https://www.googleapis.com/auth/drive'];

// Store device codes temporarily
const deviceCodes = new Map();

app.post('/device', (req, res) => {
  const userCode = uuidv4().slice(0, 8); // Generate a short userCode
  const deviceCode = uuidv4();
  
  deviceCodes.set(deviceCode, { userCode, authenticated: false });
  
  res.json({ userCode, deviceCode });
});

app.get('/auth', (req, res) => {
  const userCode = req.query.code;
  
  let deviceCode = null;
  for (const [key, value] of deviceCodes.entries()) {
    if (value.userCode === userCode) {
      deviceCode = key;
      break;
    }
  }
  
  if (!deviceCode) {
    return res.status(400).send('Invalid code');
  }
  
  const authUrl = oauth2Client.generateAuthUrl({
    access_type: 'offline',
    scope: SCOPES,
    state: deviceCode
  });
  
  res.redirect(authUrl);
});

app.get('/oauth2callback', async (req, res) => {
  const { code, state: deviceCode } = req.query;
  
  try {
    const { tokens } = await oauth2Client.getToken(code);
    oauth2Client.setCredentials(tokens);
    
    const deviceCodeData = deviceCodes.get(deviceCode);
    if (deviceCodeData) {
      deviceCodeData.authenticated = true;
      deviceCodeData.tokens = tokens;
    }
    
    res.send('Authentication successful! You can close this window.');
  } catch (error) {
    console.error('Error retrieving access token', error);
    res.status(500).send('Authentication failed');
  }
});

app.get('/token/:deviceCode', (req, res) => {
  const { deviceCode } = req.params;
  
  const deviceCodeData = deviceCodes.get(deviceCode);
  if (deviceCodeData) {
    if (deviceCodeData.authenticated) {
      deviceCodes.delete(deviceCode);
      return res.json(deviceCodeData.tokens);
    } else {
      return res.status(400).json({ error: 'authorization_pending' });
    }
  }
  
  res.status(404).json({ error: 'not_found' });
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
