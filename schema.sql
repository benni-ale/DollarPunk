CREATE TABLE IF NOT EXISTS stocks (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    date DATE NOT NULL,
    open DECIMAL(10,2),
    high DECIMAL(10,2),
    low DECIMAL(10,2),
    close DECIMAL(10,2),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, date)
);

CREATE INDEX IF NOT EXISTS idx_stocks_ticker ON stocks(ticker);
CREATE INDEX IF NOT EXISTS idx_stocks_date ON stocks(date);

CREATE TABLE IF NOT EXISTS news (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    url TEXT,
    published_at TIMESTAMP,
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_news_ticker ON news(ticker);
CREATE INDEX IF NOT EXISTS idx_news_published_at ON news(published_at); 