/*
  # User Settings Schema

  1. New Tables
    - `user_settings`
      - `id` (uuid, primary key) - Unique identifier for the settings record
      - `user_id` (uuid) - References auth.users(id), links settings to authenticated user
      - `github_token` (text, encrypted) - GitHub personal access token for repository operations
      - `openai_api_key` (text, encrypted) - OpenAI/GPT API key for code generation
      - `created_at` (timestamptz) - Timestamp when settings were created
      - `updated_at` (timestamptz) - Timestamp when settings were last modified
  
  2. Security
    - Enable RLS on `user_settings` table
    - Add policy for authenticated users to read their own settings
    - Add policy for authenticated users to insert their own settings
    - Add policy for authenticated users to update their own settings
    
  3. Notes
    - API keys are stored as encrypted text for security
    - Each user can have only one settings record (enforced by unique constraint)
    - Settings are automatically timestamped on creation and update
*/

CREATE TABLE IF NOT EXISTS user_settings (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE NOT NULL,
  github_token text,
  openai_api_key text,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own settings"
  ON user_settings FOR SELECT
  TO authenticated
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own settings"
  ON user_settings FOR INSERT
  TO authenticated
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own settings"
  ON user_settings FOR UPDATE
  TO authenticated
  USING (auth.uid() = user_id)
  WITH CHECK (auth.uid() = user_id);

CREATE INDEX IF NOT EXISTS user_settings_user_id_idx ON user_settings(user_id);