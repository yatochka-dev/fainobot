/*
  Warnings:

  - You are about to drop the column `collectFixedAmount` on the `Role` table. All the data in the column will be lost.
  - You are about to drop the column `collectPercentageAmount` on the `Role` table. All the data in the column will be lost.
  - You are about to drop the column `collectType` on the `Role` table. All the data in the column will be lost.

*/
-- CreateEnum
CREATE TYPE "RoleIncomeType" AS ENUM ('fixed', 'percentage', 'noIncome');

-- CreateEnum
CREATE TYPE "RoleIncomePlace" AS ENUM ('cash', 'bank');

-- AlterTable
ALTER TABLE "Role" DROP COLUMN "collectFixedAmount",
DROP COLUMN "collectPercentageAmount",
DROP COLUMN "collectType",
ADD COLUMN     "income" JSON NOT NULL DEFAULT '{ "type": "noIncome", "place": "bank", "amount": 100, "cooldown": 60}';

-- DropEnum
DROP TYPE "CollectType";
