/*
  Warnings:

  - You are about to drop the column `income` on the `Role` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "Role" DROP COLUMN "income",
ADD COLUMN     "incomeSettings_" JSON NOT NULL DEFAULT '{ "enabled": false, "place": "bank", "amount": 100, "cooldown": 60}';
