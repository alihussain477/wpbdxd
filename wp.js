// node_server/wp.js
const express = require('express');
const { makeWASocket, useMultiFileAuthState, fetchLatestBaileysVersion, DisconnectReason } = require('@whiskeysockets/baileys');
const fs = require('fs');
const P = require('pino');

const app = express();
app.use(express.json());

let sock;

app.get('/qr', async (req, res) => {
    const { state, saveCreds } = await useMultiFileAuthState('./auth');
    const { version } = await fetchLatestBaileysVersion();

    sock = makeWASocket({
        version,
        logger: P({ level: 'silent' }),
        printQRInTerminal: false,
        auth: state,
    });

    sock.ev.on('connection.update', ({ connection, qr }) => {
        if (qr) {
            res.send({ qr });
        }
        if (connection === 'open') {
            console.log('✅ WhatsApp connected!');
        }
    });

    sock.ev.on('creds.update', saveCreds);
});

app.post('/send', async (req, res) => {
    if (!sock) return res.send({ status: 'error', msg: 'Not connected to WhatsApp' });

    const { target, message, delay } = req.body;

    const messages = message.split('\n').filter(Boolean);
    for (let i = 0; i < messages.length; i++) {
        await sock.sendMessage(target + '@s.whatsapp.net', { text: messages[i] });
        console.log(`Sent: ${messages[i]}`);
        await new Promise(resolve => setTimeout(resolve, delay * 1000));
    }

    res.send({ status: 'success', msg: 'All messages sent.' });
});

app.listen(5001, () => console.log('📡 Node server running on http://localhost:5001'));
