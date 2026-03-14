//! AegisFlow — Compliance registry on native Solana (Anchor).
//! Whitelist/blacklist and AML limits; deploy to Solana Devnet.

use anchor_lang::prelude::*;

declare_id!("AegisF1ow11111111111111111111111111111111");

const MAX_LIST_LEN: usize = 64;
const SECONDS_PER_DAY: i64 = 86400;

#[program]
pub mod aegisflow {
    use super::*;

    pub fn init_config(
        ctx: Context<InitConfig>,
        max_per_tx: u64,
        max_daily_volume: u64,
    ) -> Result<()> {
        let config = &mut ctx.accounts.config;
        config.authority = ctx.accounts.authority.key();
        config.compliance_officer = ctx.accounts.authority.key();
        config.ai_agent = ctx.accounts.authority.key();
        config.max_per_tx = max_per_tx;
        config.max_daily_volume = max_daily_volume;
        config.daily_volume_used = 0;
        config.daily_volume_reset_time = Clock::get()?.unix_timestamp;
        config.paused = false;
        config.bump = ctx.bumps.config;
        Ok(())
    }

    pub fn add_to_whitelist(ctx: Context<ComplianceOnly>, address: Pubkey) -> Result<()> {
        let config = &mut ctx.accounts.config;
        require!(!config.paused, AegisflowError::Paused);
        require!(address != Pubkey::default(), AegisflowError::ZeroAddress);
        require!(!config.blacklist.contains(&address), AegisflowError::Blacklisted);
        if !config.whitelist.contains(&address) {
            require!(config.whitelist.len() < MAX_LIST_LEN, AegisflowError::ListFull);
            config.whitelist.push(address);
        }
        Ok(())
    }

    pub fn remove_from_whitelist(ctx: Context<ComplianceOnly>, address: Pubkey) -> Result<()> {
        let config = &mut ctx.accounts.config;
        config.whitelist.retain(|&x| x != address);
        Ok(())
    }

    pub fn add_to_blacklist(ctx: Context<ComplianceOnly>, address: Pubkey) -> Result<()> {
        let config = &mut ctx.accounts.config;
        require!(address != Pubkey::default(), AegisflowError::ZeroAddress);
        config.whitelist.retain(|&x| x != address);
        if !config.blacklist.contains(&address) {
            require!(config.blacklist.len() < MAX_LIST_LEN, AegisflowError::ListFull);
            config.blacklist.push(address);
        }
        Ok(())
    }

    pub fn set_limits(ctx: Context<OwnerOnly>, max_per_tx: u64, max_daily_volume: u64) -> Result<()> {
        let config = &mut ctx.accounts.config;
        config.max_per_tx = max_per_tx;
        config.max_daily_volume = max_daily_volume;
        Ok(())
    }

    pub fn set_vault(ctx: Context<OwnerOnly>, vault: Pubkey) -> Result<()> {
        let config = &mut ctx.accounts.config;
        config.vault = vault;
        Ok(())
    }

    pub fn set_paused(ctx: Context<OwnerOnly>, paused: bool) -> Result<()> {
        ctx.accounts.config.paused = paused;
        Ok(())
    }

    pub fn record_volume(ctx: Context<RecordVolume>, amount: u64) -> Result<()> {
        let config = &mut ctx.accounts.config;
        let now = Clock::get()?.unix_timestamp;
        if now >= config.daily_volume_reset_time + SECONDS_PER_DAY {
            config.daily_volume_reset_time = now;
            config.daily_volume_used = 0;
        }
        config.daily_volume_used = config
            .daily_volume_used
            .checked_add(amount)
            .ok_or(AegisflowError::Overflow)?;
        require!(
            config.daily_volume_used <= config.max_daily_volume,
            AegisflowError::DailyLimitExceeded
        );
        Ok(())
    }
}

/// Space: 8 (disc) + 32*4 + (4+MAX_LIST_LEN*32)*2 + 8*4 + 1 + 1
const CONFIG_SPACE: usize = 8 + 128 + (4 + MAX_LIST_LEN * 32) * 2 + 32 + 2;

#[account]
pub struct ComplianceConfig {
    pub authority: Pubkey,
    pub compliance_officer: Pubkey,
    pub ai_agent: Pubkey,
    pub vault: Pubkey,
    pub whitelist: Vec<Pubkey>,
    pub blacklist: Vec<Pubkey>,
    pub max_per_tx: u64,
    pub max_daily_volume: u64,
    pub daily_volume_used: u64,
    pub daily_volume_reset_time: i64,
    pub paused: bool,
    pub bump: u8,
}

#[derive(Accounts)]
pub struct InitConfig<'info> {
    #[account(
        init,
        payer = authority,
        space = CONFIG_SPACE,
        seeds = [b"compliance"],
        bump
    )]
    pub config: Account<'info, ComplianceConfig>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ComplianceOnly<'info> {
    #[account(
        mut,
        seeds = [b"compliance"],
        bump = config.bump,
        constraint = config.compliance_officer == authority.key() || config.authority == authority.key() @ AegisflowError::Unauthorized
    )]
    pub config: Account<'info, ComplianceConfig>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct OwnerOnly<'info> {
    #[account(
        mut,
        seeds = [b"compliance"],
        bump = config.bump,
        constraint = config.authority == authority.key() @ AegisflowError::Unauthorized
    )]
    pub config: Account<'info, ComplianceConfig>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct RecordVolume<'info> {
    #[account(
        mut,
        seeds = [b"compliance"],
        bump = config.bump,
        constraint = config.vault == authority.key() || config.ai_agent == authority.key() || config.authority == authority.key() @ AegisflowError::Unauthorized
    )]
    pub config: Account<'info, ComplianceConfig>,

    pub authority: Signer<'info>,
}

#[error_code]
pub enum AegisflowError {
    #[msg("Unauthorized")]
    Unauthorized,
    #[msg("Paused")]
    Paused,
    #[msg("Zero address")]
    ZeroAddress,
    #[msg("Address is blacklisted")]
    Blacklisted,
    #[msg("List full")]
    ListFull,
    #[msg("Daily limit exceeded")]
    DailyLimitExceeded,
    #[msg("Overflow")]
    Overflow,
}
