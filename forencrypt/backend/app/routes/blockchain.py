from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session


from app.core.database import get_db
from app.models.blockchain import BlockchainBlock
from app.services.blockchain import generate_block_hash

router = APIRouter(
    prefix="/blockchain",
    tags=["Blockchain"]
)


@router.get("/chain")
def get_blockchain(
    db: Session = Depends(get_db)
):

    blocks = db.query(
        BlockchainBlock
    ).order_by(
        BlockchainBlock.block_index
    ).all()

    return blocks


@router.get("/verify")
@router.get("/verify")
def verify_blockchain(
    db: Session = Depends(get_db)
):

    blocks = db.query(
        BlockchainBlock
    ).order_by(
        BlockchainBlock.block_index
    ).all()

    if not blocks:

        return {
            "valid": True,
            "message": "Blockchain is empty"
        }

    for i, block in enumerate(blocks):

        # -----------------------------
        # 1. Verify previous hash link
        # -----------------------------

        if i == 0:

            expected_previous_hash = "0" * 64

        else:

            previous_block = blocks[i - 1]

            expected_previous_hash = previous_block.block_hash


        if block.previous_hash != expected_previous_hash:

            return {
                "valid": False,
                "message": (
                    f"Blockchain link tampered "
                    f"at block {block.block_index}"
                )
            }


        # -----------------------------
        # 2. Recalculate block hash
        # -----------------------------

        recalculated_hash = generate_block_hash(

            block_index=block.block_index,

            evidence_id=block.evidence_id,

            action=block.action,

            performed_by=block.performed_by,

            evidence_hash=block.evidence_hash,

            previous_hash=block.previous_hash
        )


        # -----------------------------
        # 3. Compare hashes
        # -----------------------------

        if recalculated_hash != block.block_hash:

            return {
                "valid": False,
                "message": (
                    f"Block data tampered "
                    f"at block {block.block_index}"
                ),
                "stored_hash": block.block_hash,
                "recalculated_hash": recalculated_hash
            }


    return {
        "valid": True,
        "message": "Blockchain integrity verified successfully",
        "total_blocks": len(blocks)
    }