# С нуля до первой выплаты: 3 недели

Цель: через 3 недели — первый сабмит на Code4rena + работающий сканер (портфолио).
Деньги в нише платят за **доказанные находки**, поэтому всё ниже — про находки, не про сертификаты.

## Неделя 1 — EVM и Solidity на уровне чтения

**Ресурсы (бесплатные):**
- [Cyfrin Updraft](https://updraft.cyfrin.io) — курс Solidity + Foundry, видео, лучшее начало.
- [Solidity by Example](https://solidity-by-example.org) — справочник по каждой конструкции.

**Что выучить (по чек-листу):**
- [ ] storage vs memory, mapping, struct, array
- [ ] modifiers, require/revert, события
- [ ] msg.sender / msg.value / msg.data
- [ ] send / transfer / call — и почему call считается правильным
- [ ] fallback() и receive()
- [ ] storage layout: что хранится в слоте 0, что такое packing

**Инструменты:**
- [ ] Установить Foundry: PowerShell → `irm https://getfoundry.sh/install | iex` → `foundryup`
- [ ] `forge init hello` — поднять тестовый проект, написать 1 тест
- [ ] `anvil` — локальный форк мейннета: `anvil --fork-url <rpc>`

**Практика:** [Ethernaut](https://ethernaut.openzeppelin.com) уровни 0–5 (бесплатно, нужен кошелёк в Sepolia).

## Неделя 2 — классы уязвимостей

**База (читать + играть на Ethernaut):**
- [ ] Reentrancy (Ethernaut 9, 10)
- [ ] Overflow/underflow: Solidity <0.8 (HongCoin!) и как 0.8 это чинит (Ethernaut 6)
- [ ] Rounding / precision loss в расчётах (главный источник Medium-багов на Code4rena)
- [ ] Access control: onlyOwner, tx.origin (Ethernaut 4, 5)
- [ ] Unchecked return / unchecked низкоуровневых вызовов
- [ ] Denial of Service / gas-ловушки
- [ ] Storage collision, delegatecall (Ethernaut 6, 13, 16)

**Ресурсы:**
- [Solodit](https://solodit.xyz) — база реальных находок аудитов, читать по 30 мин/день (фильтры: Medium, rounding, slippage).
- [SWC Registry](https://swcregistry.io) — каталог слабостей.
- [Damn Vulnerable DeFi](https://www.damnvulnerabledefi.xyz) — 2–3 уровня (unstopable, naive receiver).

## Неделя 3 — первый контест

**Code4rena:**
1. Регистрация на [code4rena.com](https://code4rena.com) (бесплатно, нужен GitHub).
2. Прочитать Warden's Handbook (линк в интерфейсе после регистрации).
3. Выбрать активный контест → скачать репо → `forge build`.
4. Читать код сверху вниз, выписывать подозрительные места.
5. Первый сабмит — **QA-отчёт** принимают у новичков: lack of events, пропущенные zero-адреса, несоответствие доков коду. $100–$300.
6. Через 2–3 контеста целиться в Medium ($1k+): rounding, slippage, griefing.

**Параллельно (каждый день 30 мин):** сканер из `scanner/` — первая находка = публичный кейс = репутация.

## Где взять RPC (бесплатно)
- Public: `https://ethereum-rpc.publicnode.com`, `https://eth.llamarpc.com`
- [Alchemy/Infura](https://www.alchemy.com) free tier — стабильнее.

## Что НЕ делать
- Не тратить время на покупку курсов — весь материал бесплатен (Updraft, Ethernaut, Solodit).
- Не гнаться за "critical $100k" — статистика не в твою пользу. Система: много QA/Medium = стабильный доход + репутация.
- Не трогать чужие средства без согласования с владельцем — whitehat или ничего.
