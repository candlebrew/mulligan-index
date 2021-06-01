charProfilesSQL = '''
    CREATE TABLE IF NOT EXISTS characters (
        id SERIAL,
        nickname TEXT,
        fullname TEXT,
        pronouns TEXT,
        age TEXT,
        date TEXT,
        tribe TEXT,
        rank TEXT,
        appearance TEXT,
        personality TEXT,
        sheet TEXT,
        image TEXT,
        owner_uid BIGINT
    );'''
    
    sheetProfilesSQL = '''
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS physical INT;
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS maxphysical INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS mental INT;
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS maxmental INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS defense INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS confidence INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS fortitude INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS fortmod INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS brute INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS force INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS swimming INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS digging INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS lithe INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS lithemod INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS careful INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS contortion INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS leaping INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS throwing INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS constitution INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS conmod INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS precoup INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS mentalrecoup INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS mrecoup INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS diet INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS exposure INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS immunity INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS empathy INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS charisma INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS memory INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS reasoning INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS perform INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS self INT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS trait TEXT;
        
        ALTER TABLE characters ADD COLUMN IF NOT EXISTS inventory TEXT;
