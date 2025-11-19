"""
Token repository with specialized query methods.
"""

from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, func, or_, cast, String, text,and_
from sqlalchemy.dialects.postgresql import insert, JSONB
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
import logging

from .base_repository import BaseRepository
from ..models.token import Token

logger = logging.getLogger(__name__)


class TokenRepository(BaseRepository[Token]):
    """
    Repository for Token model operations.

    Automatically normalizes chain names to CoinGecko standard format.
    Supports both abbreviations (eth, bsc, sol) and standard names.
    """

    def __init__(self):
        super().__init__(Token)
        self._pg_trgm_available = None  # Cache for pg_trgm availability check

    async def _check_pg_trgm_available(self, session: AsyncSession) -> bool:
        """
        Check if pg_trgm extension is available in the database.

        This method caches the result to avoid repeated checks.

        Args:
            session: Database session

        Returns:
            True if pg_trgm is available, False otherwise
        """
        if self._pg_trgm_available is not None:
            return self._pg_trgm_available

        try:
            # Check if pg_trgm extension exists by querying pg_extension
            result = await session.execute(
                text("SELECT COUNT(*) FROM pg_extension WHERE extname = 'pg_trgm'")
            )
            count = result.scalar()
            self._pg_trgm_available = count > 0
        except Exception as e:
            # If check fails, assume pg_trgm is not available
            logger.debug(f"Failed to check pg_trgm availability: {e}")
            self._pg_trgm_available = False

        logger.debug(f"pg_trgm availability: {self._pg_trgm_available}")
        return self._pg_trgm_available

    def _normalize_chain(self, chain: Optional[str]) -> Optional[str]:
        """
        Normalize chain name to standard format.

        Args:
            chain: Chain name or abbreviation (e.g., 'eth', 'ethereum', 'bsc')

        Returns:
            Standardized chain name (e.g., 'ethereum', 'binance-smart-chain')
            or None if input is None

        Example:
            >>> self._normalize_chain('eth')
            'ethereum'
            >>> self._normalize_chain('bsc')
            'binance-smart-chain'
            >>> self._normalize_chain('ethereum')
            'ethereum'
        """
        if chain is None or chain == "":
            return chain
        # Lazy import to avoid circular dependency
        from ..utils.chain_config import ChainConfig
        return ChainConfig.get_standard_name(chain)

    async def get_by_address(
        self,
        session: AsyncSession,
        chain: str,
        token_address: str
    ) -> Optional[Token]:
        """
        Get token by chain and address.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Chain name or abbreviation (e.g., 'eth', 'ethereum')
            token_address: Token contract address

        Returns:
            Token instance or None

        Example:
            >>> await repo.get_by_address(session, 'eth', '0x...')  # Works!
            >>> await repo.get_by_address(session, 'ethereum', '0x...')  # Also works!
        """
        try:
            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)

            result = await session.execute(
                select(Token)
                .where(Token.chain == normalized_chain, Token.token_address == token_address)
                .options(selectinload(Token.signals))
            )
            return result.scalar_one_or_none()
        except SQLAlchemyError as e:
            logger.error(f"Error getting token {chain}:{token_address}: {e}")
            return None

    async def upsert_token(
        self,
        session: AsyncSession,
        token_data: dict
    ) -> Optional[int]:
        """
        Insert or update token information.

        Automatically normalizes chain name to standard format.

        Args:
            session: Database session
            token_data: Dictionary containing token fields
                       chain: Can be abbreviation (e.g., 'bsc') or standard name

        Returns:
            Token ID or None if failed

        Example:
            >>> data = {"chain": "bsc", "token_address": "0x..."}  # bsc auto-converts to binance-smart-chain
            >>> token_id = await repo.upsert_token(session, data)
        """
        try:
            token_address = token_data.get("token_address")
            chain = token_data.get("chain", "solana")  # Default to solana standard name

            if not token_address:
                logger.warning("Token address is required for upsert")
                return None

            # Normalize chain name
            normalized_chain = self._normalize_chain(chain)

            # Prepare upsert data
            upsert_data = {
                "token_address": token_address,
                "chain": normalized_chain,
                "name": token_data.get("name"),
                "symbol": token_data.get("symbol"),
                "description": token_data.get("description"),
                "website": token_data.get("website"),
                "telegram": token_data.get("telegram"),
                "twitter": token_data.get("twitter"),
                "decimals": token_data.get("decimals"),
                "updated_at": datetime.utcnow(),
            }

            # Remove None values
            upsert_data = {k: v for k, v in upsert_data.items() if v is not None}

            # Execute UPSERT
            stmt = insert(Token).values(upsert_data)
            stmt = stmt.on_conflict_do_update(
                index_elements=['chain', 'token_address'],
                set_=upsert_data
            )
            result = await session.execute(stmt)
            await session.flush()

            # Get token ID
            if result.inserted_primary_key:
                token_id = result.inserted_primary_key[0]
            else:
                # For updates, fetch the ID
                token_query = select(Token.id).where(
                    Token.chain == normalized_chain,
                    Token.token_address == token_address
                )
                token_result = await session.execute(token_query)
                token_id = token_result.scalar_one()

            logger.debug(f"Upserted token with ID: {token_id}")
            return token_id

        except SQLAlchemyError as e:
            logger.error(f"Error upserting token: {e}")
            return None

    async def get_recent_tokens(
        self,
        session: AsyncSession,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get recently created tokens.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            chain: Filter by chain name or abbreviation (e.g., 'eth', 'ethereum')
            limit: Maximum number of results

        Returns:
            List of tokens ordered by creation date (most recent first)

        Example:
            >>> await repo.get_recent_tokens(session, 'bsc', 50)  # Works!
        """
        try:
            query = select(Token)

            if chain:
                # Normalize chain name
                normalized_chain = self._normalize_chain(chain)
                query = query.where(Token.chain == normalized_chain)

            query = query.order_by(Token.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recent tokens: {e}")
            return []

    async def search_tokens(
        self,
        session: AsyncSession,
        search_term: str,
        chain: Optional[str] = None,
        limit: int = 20
    ) -> List[Token]:
        """
        Search tokens by symbol, name, or address.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            search_term: Search string
            chain: Filter by chain name or abbreviation (e.g., 'sol', 'solana')
            limit: Maximum number of results

        Returns:
            List of matching tokens

        Example:
            >>> await repo.search_tokens(session, "UNI", chain="eth")  # Works!
        """
        try:
            search_pattern = f"%{search_term.lower()}%"

            query = select(Token).where(
                or_(
                    Token.symbol.ilike(search_pattern),
                    Token.name.ilike(search_pattern),
                    Token.token_address.ilike(search_pattern)
                )
            )

            if chain:
                # Normalize chain name
                normalized_chain = self._normalize_chain(chain)
                query = query.where(Token.chain == normalized_chain)

            # Order by creation date (most recent first)
            query = query.order_by(Token.created_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error searching tokens: {e}")
            return []

    async def get_recently_updated_tokens(
        self,
        session: AsyncSession,
        hours: int = 24,
        chain: Optional[str] = None,
        limit: int = 100
    ) -> List[Token]:
        """
        Get recently updated tokens.

        Supports both abbreviations and standard chain names.

        Args:
            session: Database session
            hours: Time window in hours
            chain: Filter by chain name or abbreviation (e.g., 'eth', 'ethereum')
            limit: Maximum number of results

        Returns:
            List of recently updated tokens

        Example:
            >>> await repo.get_recently_updated_tokens(session, hours=24, chain='bsc')  # Works!
        """
        try:
            time_threshold = datetime.utcnow() - timedelta(hours=hours)

            query = select(Token).where(Token.updated_at >= time_threshold)

            if chain:
                # Normalize chain name
                normalized_chain = self._normalize_chain(chain)
                query = query.where(Token.chain == normalized_chain)

            query = query.order_by(Token.updated_at.desc()).limit(limit)

            result = await session.execute(query)
            return list(result.scalars().all())
        except SQLAlchemyError as e:
            logger.error(f"Error getting recently updated tokens: {e}")
            return []
        
    async def search_by_symbol(
        self,
        session: AsyncSession,
        symbol: str,
        exact: bool = True
    ) -> List[Token]:
        """
        Search tokens by symbol.

        Args:
            session: Database session
            symbol: Token symbol to search for
            exact: If True, exact match only. If False, case-insensitive LIKE match

        Returns:
            List of matching Token objects

        Example:
            # Exact match
            tokens = await repo.search_by_symbol(session, "BTC", exact=True)

            # Fuzzy match
            tokens = await repo.search_by_symbol(session, "btc", exact=False)
        """
        try:
            normalized_symbol = symbol.strip().upper()

            if exact:
                # Exact match (case-insensitive)
                stmt = select(Token).where(
                    func.upper(Token.symbol) == normalized_symbol
                )
            else:
                # LIKE match for fuzzy search
                stmt = select(Token).where(
                    func.upper(Token.symbol).like(f"%{normalized_symbol}%")
                ).limit(10)

            result = await session.execute(stmt)
            tokens = result.scalars().all()

            logger.debug(
                f"search_by_symbol('{symbol}', exact={exact}): found {len(tokens)} tokens"
            )
            return list(tokens)

        except Exception as e:
            logger.error(f"Error searching by symbol '{symbol}': {e}")
            return []


    async def search_by_name(
        self,
        session: AsyncSession,
        name: str,
        exact: bool = False
    ) -> List[Token]:
        """
        Search tokens by name.

        Args:
            session: Database session
            name: Token name to search for
            exact: If True, exact match. If False, case-insensitive LIKE match (default)

        Returns:
            List of matching Token objects

        Example:
            # Fuzzy match (default)
            tokens = await repo.search_by_name(session, "bitcoin")

            # Exact match
            tokens = await repo.search_by_name(session, "Bitcoin", exact=True)
        """
        try:
            normalized_name = name.strip()

            if exact:
                # Exact match (case-insensitive)
                stmt = select(Token).where(
                    func.lower(Token.name) == normalized_name.lower()
                )
            else:
                # LIKE match for partial matching
                stmt = select(Token).where(
                    func.lower(Token.name).like(f"%{normalized_name.lower()}%")
                ).limit(10)

            result = await session.execute(stmt)
            tokens = result.scalars().all()

            logger.debug(
                f"search_by_name('{name}', exact={exact}): found {len(tokens)} tokens"
            )
            return list(tokens)

        except Exception as e:
            logger.error(f"Error searching by name '{name}': {e}")
            return []


    async def search_by_alias(
        self,
        session: AsyncSession,
        alias: str
    ) -> List[Token]:
        """
        Search tokens by alias using JSONB containment.

        The aliases field is a JSONB array, so we use PostgreSQL's JSONB operators
        to check if the alias exists in the array.

        Args:
            session: Database session
            alias: Alias to search for

        Returns:
            List of matching Token objects

        Example:
            tokens = await repo.search_by_alias(session, "btc")
        """
        try:
            normalized_alias = alias.strip().lower()

            # Use PostgreSQL @> operator (containment) for JSONB array search
            # Cast the search value to JSONB to ensure proper type matching
            stmt = select(Token).where(
                Token.aliases.op('@>')(cast([normalized_alias], JSONB))
            )

            result = await session.execute(stmt)
            tokens = result.scalars().all()

            logger.debug(
                f"search_by_alias('{alias}'): found {len(tokens)} tokens"
            )
            return list(tokens)

        except Exception as e:
            logger.error(f"Error searching by alias '{alias}': {e}")
            return []


    async def fuzzy_search(
        self,
        session: AsyncSession,
        text: str,
        threshold: float = 0.8,
        limit: int = 10
    ) -> List[Token]:
        """
        Fuzzy search tokens using PostgreSQL trigram similarity.

        Requires the pg_trgm extension to be installed:
            CREATE EXTENSION IF NOT EXISTS pg_trgm;

        If pg_trgm is not available, falls back to LIKE matching.

        Args:
            session: Database session
            text: Text to search for
            threshold: Similarity threshold (0.0 to 1.0, default 0.8)
            limit: Maximum number of results

        Returns:
            List of matching Token objects sorted by similarity

        Example:
            # Find tokens similar to "bitcoin"
            tokens = await repo.fuzzy_search(session, "bitcon", threshold=0.7)
        """
        try:
            normalized_text = text.strip().lower()

            # Check if pg_trgm is available before attempting to use it
            pg_trgm_available = await self._check_pg_trgm_available(session)

            if pg_trgm_available:
                # Use similarity() function from pg_trgm
                # Search across symbol, name, and coingecko_id
                stmt = select(Token).where(
                    or_(
                        func.similarity(func.lower(Token.symbol), normalized_text) >= threshold,
                        func.similarity(func.lower(Token.name), normalized_text) >= threshold,
                        func.similarity(func.lower(Token.coingecko_id), normalized_text) >= threshold,
                    )
                ).order_by(
                    # Order by best similarity score
                    func.greatest(
                        func.similarity(func.lower(Token.symbol), normalized_text),
                        func.similarity(func.lower(Token.name), normalized_text),
                        func.similarity(func.lower(Token.coingecko_id), normalized_text),
                    ).desc()
                ).limit(limit)

                result = await session.execute(stmt)
                tokens = result.scalars().all()

                logger.debug(
                    f"fuzzy_search('{text}', threshold={threshold}): "
                    f"found {len(tokens)} tokens using pg_trgm"
                )
                return list(tokens)
            else:
                # Fall back to LIKE matching if pg_trgm is not available
                logger.debug(f"pg_trgm not available, using LIKE matching for fuzzy_search")

                stmt = select(Token).where(
                    or_(
                        func.lower(Token.symbol).like(f"%{normalized_text}%"),
                        func.lower(Token.name).like(f"%{normalized_text}%"),
                        func.lower(Token.coingecko_id).like(f"%{normalized_text}%"),
                    )
                ).limit(limit)

                result = await session.execute(stmt)
                tokens = result.scalars().all()

                logger.debug(
                    f"fuzzy_search('{text}'): found {len(tokens)} tokens using LIKE"
                )
                return list(tokens)

        except Exception as e:
            logger.error(f"Error in fuzzy_search('{text}'): {e}")
            return []

    # ========== BATCH OPERATIONS ==========

    async def batch_get_by_addresses(
        self,
        session: AsyncSession,
        addresses: List[tuple[str, str]]
    ) -> List[Token]:
        """
        Batch get tokens by multiple (chain, address) pairs.

        This is much more efficient than calling get_by_address() multiple times.

        Args:
            session: Database session
            addresses: List of (chain, token_address) tuples
                      Chain can be abbreviation or standard name

        Returns:
            List of Token objects found

        Example:
            >>> addresses = [
            ...     ('eth', '0x1f9840a85d5af5bf1d1762f925bdaddc4201f984'),  # UNI
            ...     ('bsc', '0x...'),
            ...     ('sol', 'oobQ3oX6ubRYMNMahG7VSCe8Z73uaQbAWFn6f22XTgo')
            ... ]
            >>> tokens = await repo.batch_get_by_addresses(session, addresses)
        """
        if not addresses:
            return []

        try:
            # Normalize all chain names
            normalized_addresses = [
                (self._normalize_chain(chain), addr)
                for chain, addr in addresses
            ]

            # Build OR conditions for all (chain, address) pairs
            conditions = []
            for chain, addr in normalized_addresses:
                conditions.append(
                    and_(Token.chain == chain, Token.token_address == addr)
                )

            stmt = select(Token).where(or_(*conditions))
            result = await session.execute(stmt)
            tokens = list(result.scalars().all())

            logger.debug(f"batch_get_by_addresses: fetched {len(tokens)} tokens")
            return tokens

        except SQLAlchemyError as e:
            logger.error(f"Error in batch_get_by_addresses: {e}")
            return []

    async def batch_search_by_symbols(
        self,
        session: AsyncSession,
        symbols: List[str],
        exact: bool = True
    ) -> List[Token]:
        """
        Batch search tokens by multiple symbols.

        Much more efficient than calling search_by_symbol() multiple times.

        Args:
            session: Database session
            symbols: List of token symbols to search for
            exact: If True, exact match only. If False, fuzzy match

        Returns:
            List of matching Token objects

        Example:
            >>> symbols = ['BTC', 'ETH', 'SOL', 'UNI']
            >>> tokens = await repo.batch_search_by_symbols(session, symbols)
        """
        if not symbols:
            return []

        try:
            # Normalize symbols
            normalized_symbols = [s.strip().upper() for s in symbols]

            if exact:
                # Exact match using IN clause
                stmt = select(Token).where(
                    func.upper(Token.symbol).in_(normalized_symbols)
                )
            else:
                # Fuzzy match using OR conditions
                conditions = [
                    func.upper(Token.symbol).like(f"%{sym}%")
                    for sym in normalized_symbols
                ]
                stmt = select(Token).where(or_(*conditions)).limit(100)

            result = await session.execute(stmt)
            tokens = list(result.scalars().all())

            logger.debug(
                f"batch_search_by_symbols: found {len(tokens)} tokens "
                f"for {len(symbols)} symbols"
            )
            return tokens

        except SQLAlchemyError as e:
            logger.error(f"Error in batch_search_by_symbols: {e}")
            return []

    async def batch_upsert_tokens(
        self,
        session: AsyncSession,
        tokens_data: List[dict]
    ) -> dict:
        """
        Batch upsert multiple tokens efficiently.

        Uses PostgreSQL's INSERT ... ON CONFLICT for efficient bulk operations.

        Args:
            session: Database session
            tokens_data: List of token data dictionaries
                        Each dict should contain at least: chain, token_address
                        Chain can be abbreviation or standard name

        Returns:
            Dictionary with statistics: {'inserted': int, 'updated': int, 'failed': int}

        Example:
            >>> tokens_data = [
            ...     {
            ...         'chain': 'eth',  # Auto-normalized to 'ethereum'
            ...         'token_address': '0x...',
            ...         'symbol': 'UNI',
            ...         'name': 'Uniswap',
            ...         'decimals': 18
            ...     },
            ...     {
            ...         'chain': 'bsc',  # Auto-normalized to 'binance-smart-chain'
            ...         'token_address': '0x...',
            ...         'symbol': 'CAKE',
            ...         'name': 'PancakeSwap'
            ...     }
            ... ]
            >>> result = await repo.batch_upsert_tokens(session, tokens_data)
            >>> print(f"Inserted: {result['inserted']}, Updated: {result['updated']}")
        """
        if not tokens_data:
            return {'inserted': 0, 'updated': 0, 'failed': 0}

        inserted = 0
        updated = 0
        failed = 0

        try:
            # Prepare all records with normalized chain names
            prepared_records = []
            for token_data in tokens_data:
                try:
                    chain = token_data.get('chain', 'solana')
                    token_address = token_data.get('token_address')

                    if not token_address:
                        logger.warning(f"Skipping token without address: {token_data}")
                        failed += 1
                        continue

                    # Normalize chain name
                    normalized_chain = self._normalize_chain(chain)

                    record = {
                        'chain': normalized_chain,
                        'token_address': token_address,
                        'name': token_data.get('name'),
                        'symbol': token_data.get('symbol'),
                        'description': token_data.get('description'),
                        'website': token_data.get('website'),
                        'telegram': token_data.get('telegram'),
                        'twitter': token_data.get('twitter'),
                        'decimals': token_data.get('decimals'),
                        'coingecko_id': token_data.get('coingecko_id'),
                        'platforms': token_data.get('platforms'),
                        'aliases': token_data.get('aliases'),
                        'updated_at': datetime.utcnow(),
                    }

                    # Remove None values
                    record = {k: v for k, v in record.items() if v is not None}
                    prepared_records.append(record)

                except Exception as e:
                    logger.error(f"Error preparing token data: {e}")
                    failed += 1

            if not prepared_records:
                return {'inserted': 0, 'updated': 0, 'failed': failed}

            # Batch upsert using PostgreSQL INSERT ... ON CONFLICT
            stmt = insert(Token).values(prepared_records)

            # Update all fields on conflict except chain and token_address
            update_dict = {
                k: stmt.excluded[k]
                for k in prepared_records[0].keys()
                if k not in ['chain', 'token_address']
            }

            stmt = stmt.on_conflict_do_update(
                index_elements=['chain', 'token_address'],
                set_=update_dict
            )

            result = await session.execute(stmt)
            await session.flush()

            # PostgreSQL doesn't easily tell us insert vs update counts
            # We'll estimate: rowcount represents affected rows
            affected = result.rowcount
            inserted = affected  # Simplification for now

            logger.info(
                f"batch_upsert_tokens: processed {len(prepared_records)} tokens, "
                f"affected {affected} rows, failed {failed}"
            )

            return {
                'inserted': inserted,
                'updated': 0,  # Can't easily distinguish in batch
                'failed': failed,
                'total_processed': len(prepared_records)
            }

        except SQLAlchemyError as e:
            logger.error(f"Error in batch_upsert_tokens: {e}")
            return {
                'inserted': inserted,
                'updated': updated,
                'failed': failed + len(tokens_data)
            }

    async def batch_search_tokens(
        self,
        session: AsyncSession,
        search_terms: List[str],
        chain: Optional[str] = None,
        limit_per_term: int = 5
    ) -> dict[str, List[Token]]:
        """
        Batch search tokens by multiple search terms.

        Returns results grouped by search term.

        Args:
            session: Database session
            search_terms: List of search strings
            chain: Optional filter by chain (supports abbreviations)
            limit_per_term: Max results per search term

        Returns:
            Dictionary mapping search_term -> List[Token]

        Example:
            >>> terms = ['BTC', 'ethereum', 'solana']
            >>> results = await repo.batch_search_tokens(session, terms, chain='eth')
            >>> print(f"BTC results: {len(results['BTC'])}")
        """
        if not search_terms:
            return {}

        results = {}
        normalized_chain = self._normalize_chain(chain) if chain else None

        try:
            # Build combined search query for all terms
            for term in search_terms:
                search_pattern = f"%{term.lower()}%"

                query = select(Token).where(
                    or_(
                        Token.symbol.ilike(search_pattern),
                        Token.name.ilike(search_pattern),
                        Token.token_address.ilike(search_pattern)
                    )
                )

                if normalized_chain:
                    query = query.where(Token.chain == normalized_chain)

                query = query.order_by(Token.created_at.desc()).limit(limit_per_term)

                result = await session.execute(query)
                results[term] = list(result.scalars().all())

            total_results = sum(len(tokens) for tokens in results.values())
            logger.debug(
                f"batch_search_tokens: found {total_results} total results "
                f"for {len(search_terms)} terms"
            )

            return results

        except SQLAlchemyError as e:
            logger.error(f"Error in batch_search_tokens: {e}")
            return {term: [] for term in search_terms}

