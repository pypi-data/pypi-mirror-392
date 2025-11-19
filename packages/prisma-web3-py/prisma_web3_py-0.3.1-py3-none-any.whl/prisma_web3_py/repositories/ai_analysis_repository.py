"""
AI Analysis Repository - Unified repository for all AI analysis results.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy import select, and_, func, text, cast, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.dialects.postgresql import JSONB
import logging

from ..models.ai_analysis_result import AIAnalysisResult
from .base_repository import BaseRepository

logger = logging.getLogger(__name__)


class AIAnalysisRepository(BaseRepository[AIAnalysisResult]):
    """
    AI Analysis Result Repository

    Provides unified interface for querying, creating, and updating AI analysis results
    from all sources (Twitter, News, Telegram, etc.)
    """

    def __init__(self):
        super().__init__(AIAnalysisResult)

    # ========== CREATE METHODS ==========

    async def create_twitter_analysis(
        self,
        session: AsyncSession,
        tweet_id: str,
        tweet_text: str,
        user_name: str,
        user_group: Optional[str] = None,
        tweet_link: Optional[str] = None,
        tokens: Optional[List[Dict]] = None,
        analysis: Optional[Dict] = None,
        should_notify: bool = False,
        model_name: str = 'deepseek/deepseek-v3.2-exp',
        analysis_version: str = 'v1.0'
    ) -> Optional[AIAnalysisResult]:
        """
        Create or update Twitter analysis result.

        Args:
            session: Database session
            tweet_id: Unique tweet ID
            tweet_text: Tweet text
            user_name: Username
            user_group: User group (e.g., 'KOL', 'exchange')
            tweet_link: Tweet URL
            tokens: Identified tokens list
            analysis: Analysis result dict {sentiment, confidence, summary, reason}
            should_notify: Whether to send notification
            model_name: AI model name
            analysis_version: Analysis version

        Returns:
            Created or updated AIAnalysisResult object or None
        """
        try:
            if analysis is None:
                analysis = {}

            # Check if analysis already exists
            existing = await self.get_by_source(session, 'twitter', tweet_id)

            if existing:
                # Update existing record
                existing.content_text = tweet_text
                existing.author = user_name
                existing.author_group = user_group
                existing.source_link = tweet_link
                existing.tokens = tokens or []
                existing.sentiment = analysis.get('sentiment')
                existing.confidence = analysis.get('confidence')
                existing.summary = analysis.get('summary')
                existing.reasoning = analysis.get('reason') or analysis.get('reasoning')
                existing.should_notify = should_notify
                existing.model_name = model_name
                existing.analysis_version = analysis_version
                existing.updated_at = datetime.utcnow()

                await session.flush()
                await session.refresh(existing)
                logger.debug(f"Updated Twitter analysis: ID={existing.id}, sentiment={existing.sentiment}")
                return existing
            else:
                # Create new record
                result = AIAnalysisResult(
                    source_type='twitter',
                    source_id=tweet_id,
                    source_link=tweet_link,
                    content_type='tweet',
                    content_text=tweet_text,
                    author=user_name,
                    author_group=user_group,

                    # Tokens and analysis
                    tokens=tokens or [],
                    sentiment=analysis.get('sentiment'),
                    confidence=analysis.get('confidence'),
                    summary=analysis.get('summary'),
                    reasoning=analysis.get('reason') or analysis.get('reasoning'),

                    # Notification
                    should_notify=should_notify,

                    # Metadata
                    model_name=model_name,
                    analysis_version=analysis_version
                )

                session.add(result)
                await session.flush()
                await session.refresh(result)
                logger.debug(f"Created Twitter analysis: ID={result.id}, sentiment={result.sentiment}")
                return result

        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating Twitter analysis: {e}")
            return None

    async def create_news_analysis(
        self,
        session: AsyncSession,
        news_id: int,
        news_title: str,
        news_content: str,
        source: str,
        source_link: Optional[str] = None,
        matched_currencies: Optional[List[str]] = None,
        analysis_state: Optional[Dict] = None,
        model_name: str = 'deepseek/deepseek-v3.2-exp',
        analysis_version: str = 'v1.0'
    ) -> Optional[AIAnalysisResult]:
        """
        Create or update news analysis result.

        Args:
            session: Database session
            news_id: News ID
            news_title: News title
            news_content: News content
            source: News source
            source_link: News URL
            matched_currencies: Matched currency list
            analysis_state: NewsAnalysisState dict
            model_name: AI model name
            analysis_version: Analysis version

        Returns:
            Created or updated AIAnalysisResult object or None
        """
        try:
            if analysis_state is None:
                analysis_state = {}

            # Extract analysis data from state
            analysis = analysis_state.get('analysis', {})

            # Build tokens field
            tokens = None
            if matched_currencies:
                tokens = [{'symbol': c} for c in matched_currencies]

            # Check if analysis already exists
            existing = await self.get_by_source(session, 'news', str(news_id))

            if existing:
                # Update existing record
                existing.content_text = f"{news_title}\n\n{news_content[:500]}"
                existing.author = source
                existing.source_link = source_link
                existing.tokens = tokens
                existing.category = analysis_state.get('category')
                existing.importance = analysis_state.get('importance')
                existing.sentiment = analysis.get('sentiment')
                existing.confidence = analysis.get('confidence')
                existing.summary = analysis.get('summary')
                existing.reasoning = analysis.get('reasoning')
                existing.key_points = analysis.get('key_points')
                existing.market_impact = analysis_state.get('market_impact')
                existing.event_type = analysis_state.get('event_type')
                existing.intensity = analysis_state.get('intensity')
                existing.should_notify = analysis_state.get('should_notify', False)
                existing.model_name = model_name
                existing.analysis_version = analysis_version
                existing.updated_at = datetime.utcnow()

                await session.flush()
                await session.refresh(existing)
                logger.debug(
                    f"Updated news analysis: ID={existing.id}, "
                    f"category={existing.category}, importance={existing.importance}"
                )
                return existing
            else:
                # Create new record
                result = AIAnalysisResult(
                    source_type='news',
                    source_id=str(news_id),
                    source_link=source_link,
                    content_type='news_article',
                    content_text=f"{news_title}\n\n{news_content[:500]}",
                    author=source,

                    # Tokens
                    tokens=tokens,

                    # Classification (News-specific)
                    category=analysis_state.get('category'),
                    importance=analysis_state.get('importance'),

                    # Sentiment analysis
                    sentiment=analysis.get('sentiment'),
                    confidence=analysis.get('confidence'),
                    summary=analysis.get('summary'),
                    reasoning=analysis.get('reasoning'),
                    key_points=analysis.get('key_points'),

                    # Market impact (News-specific)
                    market_impact=analysis_state.get('market_impact'),
                    event_type=analysis_state.get('event_type'),
                    intensity=analysis_state.get('intensity'),

                    # Notification
                    should_notify=analysis_state.get('should_notify', False),

                    # Metadata
                    model_name=model_name,
                    analysis_version=analysis_version
                )

                session.add(result)
                await session.flush()
                await session.refresh(result)
                logger.debug(
                    f"Created news analysis: ID={result.id}, "
                    f"category={result.category}, importance={result.importance}"
                )
                return result

        except SQLAlchemyError as e:
            logger.error(f"Error creating/updating news analysis: {e}")
            return None

    # ========== QUERY METHODS ==========

    async def get_by_source(
        self,
        session: AsyncSession,
        source_type: str,
        source_id: str
    ) -> Optional[AIAnalysisResult]:
        """
        Query analysis result by source.

        Args:
            session: Database session
            source_type: Source type 'twitter' | 'news'
            source_id: Source ID

        Returns:
            AIAnalysisResult or None
        """
        try:
            stmt = select(AIAnalysisResult).where(
                and_(
                    AIAnalysisResult.source_type == source_type,
                    AIAnalysisResult.source_id == source_id
                )
            )
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error querying analysis by source: {e}")
            return None

    async def get_recent_analyses(
        self,
        session: AsyncSession,
        source_type: Optional[str] = None,
        hours: int = 24,
        limit: int = 100
    ) -> List[AIAnalysisResult]:
        """
        Get recent analysis results.

        Args:
            session: Database session
            source_type: Optional, filter by source type
            hours: Time range in hours
            limit: Result limit

        Returns:
            List of AIAnalysisResult
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            stmt = select(AIAnalysisResult).where(
                AIAnalysisResult.created_at >= since
            )

            if source_type:
                stmt = stmt.where(AIAnalysisResult.source_type == source_type)

            stmt = stmt.order_by(AIAnalysisResult.created_at.desc()).limit(limit)

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(f"Error getting recent analyses: {e}")
            return []

    async def get_pending_notifications(
        self,
        session: AsyncSession,
        source_type: Optional[str] = None
    ) -> List[AIAnalysisResult]:
        """
        Get pending notification analysis results.

        Args:
            session: Database session
            source_type: Optional, filter by source type

        Returns:
            List of pending AIAnalysisResult
        """
        try:
            stmt = select(AIAnalysisResult).where(
                and_(
                    AIAnalysisResult.should_notify == True,
                    AIAnalysisResult.notified_at.is_(None)
                )
            )

            if source_type:
                stmt = stmt.where(AIAnalysisResult.source_type == source_type)

            stmt = stmt.order_by(AIAnalysisResult.created_at.asc())

            result = await session.execute(stmt)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(f"Error getting pending notifications: {e}")
            return []

    async def mark_as_notified(
        self,
        session: AsyncSession,
        analysis_id: int
    ) -> bool:
        """
        Mark analysis as notified.

        Args:
            session: Database session
            analysis_id: Analysis result ID

        Returns:
            Success status
        """
        try:
            stmt = select(AIAnalysisResult).where(AIAnalysisResult.id == analysis_id)
            result = await session.execute(stmt)
            analysis = result.scalar_one_or_none()

            if analysis:
                analysis.notified_at = datetime.utcnow()
                analysis.notification_sent = True
                await session.flush()
                logger.debug(f"Marked analysis {analysis_id} as notified")
                return True
            return False

        except SQLAlchemyError as e:
            logger.error(f"Error marking as notified: {e}")
            return False

    # ========== STATISTICS METHODS ==========

    async def get_sentiment_stats(
        self,
        session: AsyncSession,
        source_type: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, int]:
        """
        Get sentiment statistics.

        Args:
            session: Database session
            source_type: Optional, filter by source type
            hours: Time range in hours

        Returns:
            {'positive': 45, 'neutral': 120, 'negative': 35}
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            stmt = select(
                AIAnalysisResult.sentiment,
                func.count(AIAnalysisResult.id).label('count')
            ).where(
                AIAnalysisResult.created_at >= since
            )

            if source_type:
                stmt = stmt.where(AIAnalysisResult.source_type == source_type)

            stmt = stmt.group_by(AIAnalysisResult.sentiment)

            result = await session.execute(stmt)
            return {row.sentiment: row.count for row in result if row.sentiment}

        except SQLAlchemyError as e:
            logger.error(f"Error getting sentiment stats: {e}")
            return {}

    async def get_token_mentions(
        self,
        session: AsyncSession,
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get token mention counts using JSONB query.

        Uses PostgreSQL jsonb_array_elements to expand tokens array.

        Args:
            session: Database session
            hours: Time range in hours
            limit: Result limit

        Returns:
            [{'symbol': 'BTC', 'mentions': 45}, ...]
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            # PostgreSQL JSONB array query
            sql = text("""
                SELECT
                    token->>'symbol' as symbol,
                    COUNT(*) as mentions
                FROM "AIAnalysisResult",
                     jsonb_array_elements(tokens) as token
                WHERE created_at >= :since
                  AND tokens IS NOT NULL
                  AND tokens != '[]'::jsonb
                GROUP BY token->>'symbol'
                ORDER BY mentions DESC
                LIMIT :limit
            """)

            result = await session.execute(
                sql,
                {'since': since, 'limit': limit}
            )

            return [
                {'symbol': row.symbol, 'mentions': row.mentions}
                for row in result
                if row.symbol
            ]

        except SQLAlchemyError as e:
            logger.error(f"Error getting token mentions: {e}")
            return []

    async def get_author_stats(
        self,
        session: AsyncSession,
        source_type: str = 'twitter',
        hours: int = 24,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get author posting statistics.

        Args:
            session: Database session
            source_type: Source type
            hours: Time range in hours
            limit: Result limit

        Returns:
            [{'author': 'CZ', 'total': 15, 'positive': 10, 'negative': 2, 'neutral': 3}, ...]
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            stmt = select(
                AIAnalysisResult.author,
                func.count(AIAnalysisResult.id).label('total'),
                func.sum(
                    cast(AIAnalysisResult.sentiment == 'positive', Integer)
                ).label('positive'),
                func.sum(
                    cast(AIAnalysisResult.sentiment == 'negative', Integer)
                ).label('negative'),
                func.sum(
                    cast(AIAnalysisResult.sentiment == 'neutral', Integer)
                ).label('neutral')
            ).where(
                and_(
                    AIAnalysisResult.source_type == source_type,
                    AIAnalysisResult.created_at >= since,
                    AIAnalysisResult.author.isnot(None)
                )
            ).group_by(
                AIAnalysisResult.author
            ).order_by(
                func.count(AIAnalysisResult.id).desc()
            ).limit(limit)

            result = await session.execute(stmt)

            return [
                {
                    'author': row.author,
                    'total': row.total,
                    'positive': row.positive or 0,
                    'negative': row.negative or 0,
                    'neutral': row.neutral or 0
                }
                for row in result
            ]

        except SQLAlchemyError as e:
            logger.error(f"Error getting author stats: {e}")
            return []

    async def get_analysis_stats(
        self,
        session: AsyncSession,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get comprehensive statistics.

        Args:
            session: Database session
            hours: Time range in hours

        Returns:
            Comprehensive statistics dict
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)

            # Total count
            total_stmt = select(func.count(AIAnalysisResult.id)).where(
                AIAnalysisResult.created_at >= since
            )
            total_result = await session.execute(total_stmt)
            total = total_result.scalar()

            # By source type
            source_stmt = select(
                AIAnalysisResult.source_type,
                func.count(AIAnalysisResult.id).label('count')
            ).where(
                AIAnalysisResult.created_at >= since
            ).group_by(AIAnalysisResult.source_type)

            source_result = await session.execute(source_stmt)
            by_source = {row.source_type: row.count for row in source_result}

            # Notification stats
            notify_stmt = select(
                func.count(AIAnalysisResult.id)
            ).where(
                and_(
                    AIAnalysisResult.created_at >= since,
                    AIAnalysisResult.should_notify == True
                )
            )
            notify_result = await session.execute(notify_stmt)
            should_notify_count = notify_result.scalar()

            notified_stmt = select(
                func.count(AIAnalysisResult.id)
            ).where(
                and_(
                    AIAnalysisResult.created_at >= since,
                    AIAnalysisResult.notified_at.isnot(None)
                )
            )
            notified_result = await session.execute(notified_stmt)
            notified_count = notified_result.scalar()

            return {
                'total_analyses': total,
                'by_source': by_source,
                'should_notify': should_notify_count,
                'notified': notified_count,
                'pending_notifications': should_notify_count - notified_count,
                'hours': hours,
                'since': since.isoformat()
            }

        except SQLAlchemyError as e:
            logger.error(f"Error getting analysis stats: {e}")
            return {
                'total_analyses': 0,
                'by_source': {},
                'should_notify': 0,
                'notified': 0,
                'pending_notifications': 0,
                'hours': hours
            }

    async def search_by_token(
        self,
        session: AsyncSession,
        token_symbol: str,
        hours: Optional[int] = None,
        limit: int = 50
    ) -> List[AIAnalysisResult]:
        """
        Search analyses mentioning a specific token using JSONB @> operator.

        Args:
            session: Database session
            token_symbol: Token symbol to search
            hours: Optional time range
            limit: Result limit

        Returns:
            List of AIAnalysisResult
        """
        try:
            normalized_symbol = token_symbol.strip().upper()

            # Use PostgreSQL @> operator for JSONB containment
            query = select(AIAnalysisResult).where(
                AIAnalysisResult.tokens.op('@>')(
                    cast([{"symbol": normalized_symbol}], JSONB)
                )
            )

            if hours is not None:
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
                query = query.where(AIAnalysisResult.created_at >= time_threshold)

            query = query.order_by(AIAnalysisResult.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())

        except SQLAlchemyError as e:
            logger.error(f"Error searching by token '{token_symbol}': {e}")
            return []
