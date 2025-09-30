import express from 'express';
import dotenv from 'dotenv';
import Stripe from 'stripe';
import path from 'path';
import { fileURLToPath } from 'url';

dotenv.config();

const stripeSecretKey = process.env.STRIPE_SECRET_KEY;
const priceId = process.env.STRIPE_PRICE_ID;
const baseUrl = process.env.BASE_URL || 'http://localhost:3000';

if (!stripeSecretKey || !priceId) {
  console.error('Missing STRIPE_SECRET_KEY or STRIPE_PRICE_ID in environment.');
  process.exit(1);
}

const stripe = new Stripe(stripeSecretKey, { apiVersion: '2023-10-16' });
const app = express();

app.use(express.json());
app.use(express.urlencoded({ extended: true }));

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

app.use(express.static(path.join(__dirname, 'public')));

app.post('/api/create-checkout-session', async (req, res) => {
  try {
    const { name, email } = req.body || {};

    const session = await stripe.checkout.sessions.create({
      mode: 'payment',
      line_items: [{ price: priceId, quantity: 1 }],
      customer_email: email,
      metadata: { signup_name: name || '', signup_email: email || '' },
      success_url: `${baseUrl}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${baseUrl}/cancel.html`
    });

    return res.json({ url: session.url });
  } catch (error) {
    console.error('Stripe session error:', error?.message || error);
    return res.status(500).json({ error: 'Unable to create checkout session' });
  }
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Server listening on http://localhost:${port}`);
});
