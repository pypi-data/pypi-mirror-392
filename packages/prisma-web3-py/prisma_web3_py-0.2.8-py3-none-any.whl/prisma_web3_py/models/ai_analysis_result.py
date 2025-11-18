"""
AIAnalysisResult model - Unified storage for all AI analysis results.
"""

from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy import (
    Integer, String, Float, Boolean, DateTime, Index, UniqueConstraint, func, text
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import Mapped, mapped_column

from ..base import Base


class AIAnalysisResult(Base):
    """
    AI Analysis Result model representing all AI analysis results.

    This model stores analysis results from all sources (Twitter, News, Telegram, etc.),
    including token recognition, sentiment analysis, and market impact assessment.

    Corresponds to Prisma model: AIAnalysisResult
    Table: AIAnalysisResult
    """

    __tablename__ = "AIAnalysisResult"

    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # === Source Information ===
    source_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Source type: twitter, news, telegram, discord"
    )
    source_id: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Original data ID: tweet_id, news_id, etc."
    )
    source_link: Mapped[Optional[str]] = mapped_column(
        String,
        comment="Original content URL"
    )

    # === Content Information ===
    content_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Content type: tweet, news_article, telegram_message"
    )
    content_text: Mapped[str] = mapped_column(
        String,
        nullable=False,
        comment="Original text content (for reference)"
    )
    author: Mapped[Optional[str]] = mapped_column(
        String,
        comment="Author/username"
    )
    author_group: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="User group: KOL, exchange, whale"
    )

    # === Token Recognition (JSONB) ===
    tokens: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment='Identified tokens: [{symbol, name, chain, coingecko_id}]'
    )

    # === Sentiment Analysis (Common) ===
    sentiment: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Sentiment: positive, negative, neutral"
    )
    confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Confidence score 0.0-1.0"
    )
    summary: Mapped[Optional[str]] = mapped_column(
        String,
        comment="AI-generated summary"
    )
    reasoning: Mapped[Optional[str]] = mapped_column(
        String,
        comment="AI reasoning"
    )
    key_points: Mapped[Optional[list]] = mapped_column(
        JSON,
        server_default=text("'[]'::json"),
        comment="Key points list"
    )

    # === Classification (News-specific) ===
    category: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="News category: exchange_listing, partnership, hack, investment"
    )
    importance: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Importance level: high, medium, low"
    )

    # === Market Impact (News-specific) ===
    market_impact: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Market impact: bullish, bearish, neutral"
    )
    event_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="Event type: bullish_event, bearish_event, fud, fomo, neutral_report"
    )
    intensity: Mapped[Optional[float]] = mapped_column(
        Float,
        comment="Impact intensity 0.0-1.0"
    )

    # === Notification Management ===
    should_notify: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Whether to send notification"
    )
    notified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        comment="Actual notification time"
    )
    notification_sent: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
        comment="Notification sent status"
    )

    # === Metadata ===
    model_name: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="AI model used (e.g., 'deepseek/deepseek-v3.2-exp')"
    )
    analysis_version: Mapped[Optional[str]] = mapped_column(
        String(20),
        comment="Analysis version (for tracking model iterations)"
    )

    # === Timestamps ===
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        comment="Record creation time"
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        onupdate=func.now(),
        comment="Record update time"
    )

    # === Table constraints and indexes ===
    __table_args__ = (
        # Unique constraint: prevent duplicate analysis
        UniqueConstraint('source_type', 'source_id', name='unique_analysis_source'),

        # Regular indexes
        Index('idx_analysis_source_type_id', 'source_type', 'source_id'),
        Index('idx_analysis_created_at', 'created_at'),
        Index('idx_analysis_notify_pending', 'should_notify', 'notified_at'),
        Index('idx_analysis_sentiment', 'sentiment'),
        Index('idx_analysis_author', 'author'),

        # GIN indexes for JSONB fields
        Index('idx_analysis_tokens_gin', 'tokens', postgresql_using='gin'),
        Index('idx_analysis_key_points_gin', 'key_points', postgresql_using='gin'),

        {'schema': 'public'}
    )

    def __repr__(self):
        return (
            f"<AIAnalysisResult(id={self.id}, "
            f"type={self.source_type}, "
            f"sentiment={self.sentiment})>"
        )

    def to_dict(self) -> dict:
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "source_link": self.source_link,
            "content_type": self.content_type,
            "content_text": self.content_text,
            "author": self.author,
            "author_group": self.author_group,
            "tokens": self.tokens or [],
            "sentiment": self.sentiment,
            "confidence": self.confidence,
            "summary": self.summary,
            "reasoning": self.reasoning,
            "key_points": self.key_points or [],
            "category": self.category,
            "importance": self.importance,
            "market_impact": self.market_impact,
            "event_type": self.event_type,
            "intensity": self.intensity,
            "should_notify": self.should_notify,
            "notified_at": self.notified_at.isoformat() if self.notified_at else None,
            "notification_sent": self.notification_sent,
            "model_name": self.model_name,
            "analysis_version": self.analysis_version,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    def get_token_symbols(self) -> List[str]:
        """
        Get list of token symbols from tokens field.

        Returns:
            List of token symbols
        """
        if not self.tokens:
            return []
        return [t.get('symbol') for t in self.tokens if isinstance(t, dict) and 'symbol' in t]

    def has_token(self, symbol: str) -> bool:
        """
        Check if analysis mentions a specific token.

        Args:
            symbol: Token symbol to check

        Returns:
            True if token is mentioned
        """
        return symbol.upper() in [s.upper() for s in self.get_token_symbols()]

    def is_high_confidence(self, threshold: float = 0.7) -> bool:
        """
        Check if analysis has high confidence.

        Args:
            threshold: Confidence threshold (default 0.7)

        Returns:
            True if confidence >= threshold
        """
        return self.confidence is not None and self.confidence >= threshold

    def is_high_importance(self) -> bool:
        """
        Check if analysis is marked as high importance.

        Returns:
            True if importance is 'high'
        """
        return self.importance == 'high'
