-- AlterTable
ALTER TABLE "Guild" ADD COLUMN     "items_index" INTEGER NOT NULL DEFAULT 1;

-- AlterTable
ALTER TABLE "Item" ADD COLUMN     "index" INTEGER NOT NULL DEFAULT 1;
