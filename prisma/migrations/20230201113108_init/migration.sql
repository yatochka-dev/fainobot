-- CreateEnum
CREATE TYPE "Language" AS ENUM ('uk', 'en', 'ru');

-- CreateEnum
CREATE TYPE "MoneyAmountType" AS ENUM ('fixed', 'random');

-- CreateEnum
CREATE TYPE "CollectType" AS ENUM ('fixed', 'percentage', 'noCollect');

-- CreateTable
CREATE TABLE "Guild" (
    "snowflake" TEXT NOT NULL,
    "language" "Language" NOT NULL DEFAULT 'en',

    CONSTRAINT "Guild_pkey" PRIMARY KEY ("snowflake")
);

-- CreateTable
CREATE TABLE "User" (
    "snowflake" TEXT NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("snowflake")
);

-- CreateTable
CREATE TABLE "Member" (
    "id" SERIAL NOT NULL,
    "userId" TEXT NOT NULL,
    "guildId" TEXT NOT NULL,
    "money" INTEGER NOT NULL DEFAULT 0,
    "bank" INTEGER NOT NULL DEFAULT 0,

    CONSTRAINT "Member_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "GuildSettings" (
    "guildId" TEXT NOT NULL,
    "messageMoneyEnabled" BOOLEAN NOT NULL DEFAULT true,
    "messageMoneyAmountType" "MoneyAmountType" NOT NULL DEFAULT 'fixed',
    "messageFixedMoneyAmount" INTEGER NOT NULL DEFAULT 10,
    "messageMinMoneyAmount" INTEGER NOT NULL DEFAULT 5,
    "messageMaxMoneyAmount" INTEGER NOT NULL DEFAULT 25,
    "messageMoneyCooldown" INTEGER NOT NULL DEFAULT 60,
    "voiceMoneyEnabled" BOOLEAN NOT NULL DEFAULT true,
    "voiceMoneyAmountType" "MoneyAmountType" NOT NULL DEFAULT 'fixed',
    "voiceFixedMoneyAmount" INTEGER NOT NULL DEFAULT 10,
    "voiceMinMoneyAmount" INTEGER NOT NULL DEFAULT 5,
    "voiceMaxMoneyAmount" INTEGER NOT NULL DEFAULT 25,
    "voiceMoneyCooldown" INTEGER NOT NULL DEFAULT 60,
    "reactionMoneyEnabled" BOOLEAN NOT NULL DEFAULT true,
    "reactionMoneyAmountType" "MoneyAmountType" NOT NULL DEFAULT 'fixed',
    "reactionFixedMoneyAmount" INTEGER NOT NULL DEFAULT 10,
    "reactionMinMoneyAmount" INTEGER NOT NULL DEFAULT 5,
    "reactionMaxMoneyAmount" INTEGER NOT NULL DEFAULT 25,
    "reactionMoneyCooldown" INTEGER NOT NULL DEFAULT 60,

    CONSTRAINT "GuildSettings_pkey" PRIMARY KEY ("guildId")
);

-- CreateTable
CREATE TABLE "Role" (
    "snowflake" TEXT NOT NULL,
    "guildId" TEXT NOT NULL,
    "collectType" "CollectType" NOT NULL DEFAULT 'noCollect',
    "collectFixedAmount" INTEGER NOT NULL DEFAULT 10,
    "collectPercentageAmount" INTEGER NOT NULL DEFAULT 10,

    CONSTRAINT "Role_pkey" PRIMARY KEY ("snowflake")
);

-- CreateTable
CREATE TABLE "Item" (
    "id" SERIAL NOT NULL,
    "guildId" TEXT NOT NULL,
    "title" VARCHAR(200) NOT NULL,
    "description" TEXT,
    "replyMessage" TEXT,
    "price" INTEGER NOT NULL,
    "stock" INTEGER,
    "availableUntil" TIMESTAMP(3),

    CONSTRAINT "Item_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "InventoryItem" (
    "id" SERIAL NOT NULL,
    "originalId" INTEGER NOT NULL,
    "ownerId" INTEGER NOT NULL,

    CONSTRAINT "InventoryItem_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "InvokedSlashCommand" (
    "interaction_id" TEXT NOT NULL,
    "command_name" TEXT NOT NULL,
    "guild_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "channel_id" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "InvokedSlashCommand_pkey" PRIMARY KEY ("interaction_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "Member_userId_guildId_key" ON "Member"("userId", "guildId");

-- CreateIndex
CREATE UNIQUE INDEX "Item_guildId_title_key" ON "Item"("guildId", "title");

-- AddForeignKey
ALTER TABLE "Member" ADD CONSTRAINT "Member_userId_fkey" FOREIGN KEY ("userId") REFERENCES "User"("snowflake") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Member" ADD CONSTRAINT "Member_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("snowflake") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "GuildSettings" ADD CONSTRAINT "GuildSettings_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("snowflake") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Role" ADD CONSTRAINT "Role_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("snowflake") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Item" ADD CONSTRAINT "Item_guildId_fkey" FOREIGN KEY ("guildId") REFERENCES "Guild"("snowflake") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "InventoryItem" ADD CONSTRAINT "InventoryItem_originalId_fkey" FOREIGN KEY ("originalId") REFERENCES "Item"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "InventoryItem" ADD CONSTRAINT "InventoryItem_ownerId_fkey" FOREIGN KEY ("ownerId") REFERENCES "Member"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
